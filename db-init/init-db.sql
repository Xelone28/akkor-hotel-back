CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    pseudo VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS hotels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    description TEXT,
    rating DECIMAL(2,1),
    breakfast BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS user_hotels (
    user_id INTEGER NOT NULL,
    hotel_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, hotel_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (hotel_id) REFERENCES hotels(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hotel_pictures (
    id SERIAL PRIMARY KEY,
    hotel_id INTEGER NOT NULL,
    uuid TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hotel_id) REFERENCES hotels(id) ON DELETE CASCADE
);

-- DATA SAMPLE :

INSERT INTO hotels (name, address, description, rating, breakfast) VALUES
    ('Hilton Paris Opera', 'Paris, France', 'Luxury hotel in the heart of Paris.', 4.7, TRUE),
    ('The Plaza Hotel', 'New York, USA', 'A legendary 5-star hotel in NYC.', 4.9, TRUE),
    ('Ritz-Carlton Tokyo', 'Tokyo, Japan', 'High-end hotel with stunning skyline views.', 4.8, TRUE),
    ('Marina Bay Sands', 'Singapore', 'Iconic hotel with world-famous infinity pool.', 4.5, TRUE),
    ('Burj Al Arab', 'Dubai, UAE', 'Ultra-luxury hotel shaped like a sail.', 5.0, TRUE),
    ('Hotel Montecristo', 'Paris, France', 'Charming boutique hotel in Paris.', 4.2, FALSE),
    ('The Langham', 'London, UK', 'Historic luxury hotel in London.', 4.6, TRUE),
    ('The Peninsula', 'Bangkok, Thailand', 'Elegant riverside hotel with great ambiance.', 4.7, TRUE),
    ('JW Marriott', 'Los Angeles, USA', 'Upscale accommodation near LA Live.', 4.4, FALSE),
    ('Grand Hyatt', 'Berlin, Germany', 'A modern luxury hotel in Berlin.', 4.5, TRUE);

INSERT INTO hotels (name, address, description, rating, breakfast) VALUES
    ('Le Meurice', 'Paris, France', 'Luxury palace hotel with artistic charm.', 4.9, TRUE),
    ('Shangri-La Hotel', 'Paris, France', 'Elegant 5-star hotel with Eiffel Tower views.', 4.8, TRUE),
    ('Hotel de Crillon', 'Paris, France', 'Historic and luxurious hotel in Place de la Concorde.', 4.7, TRUE),
    ('The Peninsula Paris', 'Paris, France', 'Prestigious hotel near the Arc de Triomphe.', 4.9, TRUE),
    ('Hotel Lutetia', 'Paris, France', 'Renowned Art Deco hotel in Saint-Germain.', 4.6, TRUE);