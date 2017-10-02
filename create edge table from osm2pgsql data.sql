DROP TABLE IF EXISTS cincy_edges;
WITH sub AS (
	SELECT 
		t.id AS way_id,
		a.node_id,
		a.row_number,
		t.tags::hstore -> 'highway' AS highway,
		t.tags::hstore -> 'route' AS route, -- ferry
		t.tags::hstore -> 'service' AS service
	FROM 
		cincy_ways AS t, 
		unnest(t.nodes) WITH ORDINALITY a(node_id, row_number)
	WHERE 
		t.tags::hstore -> 'highway' IS NOT NULL OR
		t.tags::hstore -> 'route' = 'ferry'
)
SELECT 
	s1.way_id,
	s1.highway,
	ARRAY[s1.node_id,s2.node_id] AS nodes
INTO cincy_edges
FROM sub AS s1 JOIN sub AS s2
	ON s1.way_id = s2.way_id AND 
	s1.row_number = s2.row_number - 1;

-- sort the node ID's ascending, as is done in the script
UPDATE cincy_edges SET nodes = ARRAY[nodes[2],nodes[1]]
WHERE nodes[1] > nodes[2];
CREATE INDEX ON cincy_edges (nodes);
	
-- ADD COLUMNs to be used later
ALTER TABLE cincy_edges
	ADD COLUMN bicycle_count integer DEFAULT 0,
	ADD COLUMN car_count integer DEFAULT 0,
	ADD COLUMN foot_count integer DEFAULT 0,
	
	ADD COLUMN n1geom geometry(POINT,4326),
	ADD COLUMN n2geom geometry(POINT,4326),	
	ADD COLUMN edge geometry(LINESTRING,4326),
	ADD COLUMN length real;

UPDATE cincy_edges SET n1geom = geom FROM cincy_nodes WHERE nodes[1] = id;
UPDATE cincy_edges SET n2geom = geom FROM cincy_nodes WHERE nodes[2] = id;
UPDATE cincy_edges SET edge = ST_MakeLine(n1geom,n2geom);
UPDATE cincy_edges SET length = ST_Length(edge);

-- save space
ALTER TABLE cincy_edges 
	DROP COLUMN n1geom, 
	DROP COLUMN n2geom;