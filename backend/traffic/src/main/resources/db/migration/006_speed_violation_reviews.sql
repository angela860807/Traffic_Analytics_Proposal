CREATE TABLE IF NOT EXISTS speed_violation_reviews (
    review_id BIGSERIAL PRIMARY KEY,
    violation_id BIGINT NOT NULL,
    from_status VARCHAR(20) NOT NULL,
    to_status VARCHAR(20) NOT NULL,
    reason VARCHAR(120),
    memo VARCHAR(500),
    reviewed_by VARCHAR(80),
    reviewed_at TIMESTAMP NOT NULL,
    CONSTRAINT fk_speed_violation_reviews_violation
        FOREIGN KEY (violation_id)
        REFERENCES speed_violations (violation_id)
);

CREATE INDEX IF NOT EXISTS idx_speed_violation_reviews_violation
    ON speed_violation_reviews (violation_id);

CREATE INDEX IF NOT EXISTS idx_speed_violation_reviews_reviewed_at
    ON speed_violation_reviews (reviewed_at);
