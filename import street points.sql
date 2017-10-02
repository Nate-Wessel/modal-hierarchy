DROP TABLE IF EXISTS street_points;
CREATE TABLE street_points (
	x real,
	y real,
	geom geometry(Point,4326)
);
COPY street_points (x,y) FROM '/home/nate/GTABM/street-points.csv' CSV HEADER;
UPDATE street_points SET geom = ST_Transform( ST_SetSRID(ST_MakePoint(x,y),32616),4326);