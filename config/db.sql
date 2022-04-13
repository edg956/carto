CREATE TABLE IT NO EXISTS PostalCodes (
    the_geom TEXT NOT NULL,
    code CHAR(5) NOT NULL,
    id INT NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IT NO EXISTS Payments (
    amount DECIMAL NOT NULL,
    p_month DATE NOT NULL,
    p_age VARCHAR(8) NOT NULL,
    p_gender CHAR(1) NOT NULL,
    postal_code_id INT NOT NULL,
    id INT NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_postal_code_id
        FOREIGN KEY (postal_code_id)
        REFERENCES PostalCodes (id)
);
