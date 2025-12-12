CREATE TABLE price_data (
    datetime TIMESTAMP PRIMARY KEY,
    open DECIMAL,
    high DECIMAL,
    low DECIMAL,
    close DECIMAL,
    volume INTEGER
);
select * from price_data
DROP TABLE IF EXISTS price_data;