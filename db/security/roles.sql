-- ============================================================
-- roles.sql
-- DB 계정·권한 분리
-- 기준: 08_DB_작업_TODO.md
--
-- 역할:
--   traffic_migrator  : migration 전용 (DDL)
--   traffic_app       : Spring Boot DML 전용
--   traffic_readonly  : AI 모델 export 읽기 전용
--
-- 비밀번호는 SQL에 기록하지 않고
-- Docker Compose 또는 환경변수로 주입
-- ============================================================

-- ------------------------------------------------------------
-- 1. 역할 생성
-- ------------------------------------------------------------
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'traffic_migrator') THEN
        CREATE ROLE traffic_migrator LOGIN;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'traffic_app') THEN
        CREATE ROLE traffic_app LOGIN;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'traffic_readonly') THEN
        CREATE ROLE traffic_readonly LOGIN;
    END IF;
END $$;

-- ------------------------------------------------------------
-- 2. traffic_migrator 권한
--    migration 파일 적용 전용
-- ------------------------------------------------------------
GRANT CONNECT ON DATABASE traffic TO traffic_migrator;
GRANT USAGE, CREATE ON SCHEMA public TO traffic_migrator;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO traffic_migrator;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO traffic_migrator;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT ALL ON TABLES TO traffic_migrator;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT ALL ON SEQUENCES TO traffic_migrator;

-- ------------------------------------------------------------
-- 3. traffic_app 권한
--    Spring Boot DML 전용 (DDL 불가)
-- ------------------------------------------------------------
GRANT CONNECT ON DATABASE traffic TO traffic_app;
GRANT USAGE ON SCHEMA public TO traffic_app;

-- DML만 허용 (DDL 제외)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO traffic_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO traffic_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO traffic_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO traffic_app;

-- schema DDL 권한 명시적 제거
REVOKE CREATE ON SCHEMA public FROM traffic_app;

-- ------------------------------------------------------------
-- 4. traffic_readonly 권한
--    AI 모델 export 읽기 전용
--    번호판·회원 정보 접근 차단
-- ------------------------------------------------------------
GRANT CONNECT ON DATABASE traffic TO traffic_readonly;
GRANT USAGE ON SCHEMA public TO traffic_readonly;

-- 전체 테이블 읽기 허용
GRANT SELECT ON ALL TABLES IN SCHEMA public TO traffic_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO traffic_readonly;

-- 번호판·회원 정보 접근 차단
REVOKE SELECT ON vehicles FROM traffic_readonly;
REVOKE SELECT ON members FROM traffic_readonly;
REVOKE SELECT ON detection_analysis_results FROM traffic_readonly;
REVOKE SELECT ON speed_violations FROM traffic_readonly;
REVOKE SELECT ON speed_violation_reviews FROM traffic_readonly;

-- camera_health_samples 읽기는 허용 (AI 학습용)
GRANT SELECT ON camera_health_samples TO traffic_readonly;
GRANT SELECT ON traffic_context_samples TO traffic_readonly;
GRANT SELECT ON anomaly_events TO traffic_readonly;
GRANT SELECT ON model_prediction_logs TO traffic_readonly;

-- ------------------------------------------------------------
-- 5. public schema 불필요한 CREATE 권한 제거
-- ------------------------------------------------------------
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

-- ------------------------------------------------------------
-- 6. 권한 확인 쿼리
-- ------------------------------------------------------------
SELECT
    grantee,
    table_name,
    privilege_type
FROM information_schema.role_table_grants
WHERE grantee IN ('traffic_migrator','traffic_app','traffic_readonly')
ORDER BY grantee, table_name, privilege_type;
