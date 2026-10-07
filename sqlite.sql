
CREATE TABLE IF NOT EXISTS lost_items(id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT NOT NULL, category TEXT NOT NULL, brand TEXT NOT NULL, color TEXT NOT NULL, location_found TEXT NOT NULL, date_found DATE NOT NULL, image BLOB NOT NULL); -- Better to use capital letters, even through sqlite is not case sensitive 

-- AUTOINCREMENT -> This tells the database to create the id for you.
-- INSERT INTO lost_items(item_name, category,..
-- VALUES (connect this to the class, the forms that people fill out. 
-- SELECT * FROM lost_items 

DROP TABLE IF EXISTS  claims; 


