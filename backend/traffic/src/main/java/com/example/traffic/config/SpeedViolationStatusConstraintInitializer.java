package com.example.traffic.config;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import javax.sql.DataSource;
import java.sql.Connection;

@Slf4j
@Component
@RequiredArgsConstructor
public class SpeedViolationStatusConstraintInitializer implements ApplicationRunner {

    private static final String DROP_STATUS_CHECK_CONSTRAINTS = """
            DO $$
            DECLARE
                constraint_record record;
            BEGIN
                FOR constraint_record IN
                    SELECT conname
                    FROM pg_constraint
                    WHERE conrelid = 'speed_violations'::regclass
                      AND contype = 'c'
                      AND pg_get_constraintdef(oid) ILIKE '%violation_status%'
                LOOP
                    EXECUTE format(
                        'ALTER TABLE speed_violations DROP CONSTRAINT IF EXISTS %I',
                        constraint_record.conname
                    );
                END LOOP;
            END $$;
            """;

    private static final String ADD_STATUS_CHECK_CONSTRAINT = """
            ALTER TABLE speed_violations
            ADD CONSTRAINT speed_violations_violation_status_check
            CHECK (violation_status IN ('UNPROCESSED', 'NOTIFIED', 'REJECTED', 'CLOSED'))
            """;

    private final DataSource dataSource;
    private final JdbcTemplate jdbcTemplate;

    @Override
    public void run(ApplicationArguments args) throws Exception {
        if (!isPostgreSql()) {
            return;
        }

        jdbcTemplate.execute(DROP_STATUS_CHECK_CONSTRAINTS);
        jdbcTemplate.execute(ADD_STATUS_CHECK_CONSTRAINT);
        log.info("speed_violations.violation_status check constraint synchronized.");
    }

    private boolean isPostgreSql() throws Exception {
        try (Connection connection = dataSource.getConnection()) {
            String productName = connection.getMetaData().getDatabaseProductName();
            return productName != null && productName.toLowerCase().contains("postgresql");
        }
    }
}
