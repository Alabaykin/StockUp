CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE Families (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invite_code VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Users (
    telegram_id BIGINT PRIMARY KEY,
    family_id UUID REFERENCES Families(id) ON DELETE SET NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    family_id UUID NOT NULL REFERENCES Families(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE Products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    family_id UUID NOT NULL REFERENCES Families(id) ON DELETE CASCADE,
    category_id UUID REFERENCES Categories(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    lemma VARCHAR(255) NOT NULL,
    emoji VARCHAR(10),
    description TEXT,
    quantity NUMERIC(10, 2) DEFAULT 0,
    unit VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_family ON Products(family_id);

CREATE TABLE Product_Subscriptions (
    user_id BIGINT REFERENCES Users(telegram_id) ON DELETE CASCADE,
    product_id UUID REFERENCES Products(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, product_id)
);
