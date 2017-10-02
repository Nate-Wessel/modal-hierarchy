ALTER TABLE oxford_nodes ADD COLUMN geom geometry(POINT,4326);
UPDATE oxford_nodes SET geom = ST_SetSRID( 
	ST_MakePoint(lon/10000000.0,lat/10000000.0),
	4326
);