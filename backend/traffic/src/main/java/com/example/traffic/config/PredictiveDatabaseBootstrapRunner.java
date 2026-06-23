package com.example.traffic.config;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.core.annotation.Order;
import org.springframework.core.io.Resource;
import org.springframework.core.io.ResourceLoader;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import javax.sql.DataSource;
import java.sql.Connection;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

@Slf4j
@Component
@RequiredArgsConstructor
@Order(100)
public class PredictiveDatabaseBootstrapRunner implements ApplicationRunner {

    private static final List<String> MIGRATION_LOCATIONS = List.of(
            "classpath:db/migration/001_backend_schema_updates.sql",
            "classpath:db/migration/002_cleanup_detection_logs_legacy_columns.sql",
            "classpath:db/migration/003_detection_type_unknown_and_analysis_index.sql",
            "classpath:db/migration/004_make_flow_metrics_nullable_until_estimated.sql",
            "classpath:db/migration/005_speed_violation_status_values.sql",
            "classpath:db/migration/006_speed_violation_reviews.sql",
            "classpath:db/migration/007_predictive_maintenance_schema.sql",
            "classpath:db/migration/008_predictive_seed_policies.sql",
            "classpath:db/migration/009_predictive_ticket_history_backfill.sql"
    );

    private static final List<String> SEED_LOCATIONS = List.of(
            "classpath:db/seed/demo_seed.sql",
            "classpath:db/seed/commercial_demo_seed.sql"
    );

    private final DataSource dataSource;
    private final JdbcTemplate jdbcTemplate;
    private final ResourceLoader resourceLoader;

    @Value("${app.db.bootstrap.enabled:false}")
    private boolean enabled;

    @Value("${app.db.bootstrap.seed-demo:true}")
    private boolean seedDemo;

    @Value("${app.db.bootstrap.force-seed:false}")
    private boolean forceSeed;

    @Override
    public void run(ApplicationArguments args) throws Exception {
        if (!enabled) {
            return;
        }
        if (!isPostgreSql()) {
            log.info("Predictive DB bootstrap skipped: database is not PostgreSQL.");
            return;
        }

        log.info("Predictive DB bootstrap started.");
        for (String location : MIGRATION_LOCATIONS) {
            executeSql(location);
        }

        if (seedDemo && shouldApplyDemoSeed()) {
            for (String location : SEED_LOCATIONS) {
                executeSql(location);
            }
        } else {
            log.info("Predictive demo seed skipped. seedDemo={}, forceSeed={}", seedDemo, forceSeed);
        }
        log.info("Predictive DB bootstrap finished.");
    }

    private boolean shouldApplyDemoSeed() {
        if (forceSeed) {
            return true;
        }
        Integer count = jdbcTemplate.queryForObject("""
                SELECT COUNT(*)
                FROM camera_health_samples
                WHERE idempotency_key LIKE 'demo-bl-%'
                   OR idempotency_key LIKE 'commercial-bl-%'
                """, Integer.class);
        return count == null || count == 0;
    }

    private void executeSql(String location) throws Exception {
        Resource resource = resourceLoader.getResource(location);
        String sql = new String(resource.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
        for (String statement : splitSqlStatements(sql)) {
            jdbcTemplate.execute(statement);
        }
        log.info("Applied SQL resource: {}", location);
    }

    private List<String> splitSqlStatements(String sql) {
        List<String> statements = new ArrayList<>();
        StringBuilder current = new StringBuilder();
        boolean singleQuote = false;
        boolean doubleQuote = false;
        boolean lineComment = false;
        boolean blockComment = false;
        String dollarQuoteTag = null;

        for (int i = 0; i < sql.length(); i++) {
            char c = sql.charAt(i);
            char next = i + 1 < sql.length() ? sql.charAt(i + 1) : '\0';

            if (lineComment) {
                current.append(c);
                if (c == '\n') {
                    lineComment = false;
                }
                continue;
            }

            if (blockComment) {
                current.append(c);
                if (c == '*' && next == '/') {
                    current.append(next);
                    i++;
                    blockComment = false;
                }
                continue;
            }

            if (dollarQuoteTag != null) {
                if (sql.startsWith(dollarQuoteTag, i)) {
                    current.append(dollarQuoteTag);
                    i += dollarQuoteTag.length() - 1;
                    dollarQuoteTag = null;
                } else {
                    current.append(c);
                }
                continue;
            }

            if (singleQuote) {
                current.append(c);
                if (c == '\'' && next == '\'') {
                    current.append(next);
                    i++;
                } else if (c == '\'') {
                    singleQuote = false;
                }
                continue;
            }

            if (doubleQuote) {
                current.append(c);
                if (c == '"' && next == '"') {
                    current.append(next);
                    i++;
                } else if (c == '"') {
                    doubleQuote = false;
                }
                continue;
            }

            if (c == '-' && next == '-') {
                current.append(c).append(next);
                i++;
                lineComment = true;
                continue;
            }

            if (c == '/' && next == '*') {
                current.append(c).append(next);
                i++;
                blockComment = true;
                continue;
            }

            if (c == '\'') {
                current.append(c);
                singleQuote = true;
                continue;
            }

            if (c == '"') {
                current.append(c);
                doubleQuote = true;
                continue;
            }

            String tag = readDollarQuoteTag(sql, i);
            if (tag != null) {
                current.append(tag);
                i += tag.length() - 1;
                dollarQuoteTag = tag;
                continue;
            }

            if (c == ';') {
                current.append(c);
                String statement = current.toString().trim();
                if (!statement.isEmpty()) {
                    statements.add(statement);
                }
                current.setLength(0);
                continue;
            }

            current.append(c);
        }

        String tail = current.toString().trim();
        if (!tail.isEmpty()) {
            statements.add(tail);
        }
        return statements;
    }

    private String readDollarQuoteTag(String sql, int start) {
        if (sql.charAt(start) != '$') {
            return null;
        }
        int end = sql.indexOf('$', start + 1);
        if (end < 0) {
            return null;
        }
        String tagName = sql.substring(start + 1, end);
        if (!tagName.isEmpty() && !tagName.matches("[A-Za-z_][A-Za-z0-9_]*")) {
            return null;
        }
        return sql.substring(start, end + 1);
    }

    private boolean isPostgreSql() throws Exception {
        try (Connection connection = dataSource.getConnection()) {
            String productName = connection.getMetaData().getDatabaseProductName();
            return productName != null && productName.toLowerCase().contains("postgresql");
        }
    }
}
