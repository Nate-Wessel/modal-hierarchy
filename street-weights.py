# generate random points along the street network
# to be used as origins and destinations for routing

import psycopg2, random, math
from shapely.wkb import loads as loadWKB, dumps as dumpWKB

# connect to the DB
conn_string = ("host='localhost' dbname='osm' user='nate' password=''")
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

print 'getting all the streets'
cursor.execute("""
	SELECT 
		-- local geometry in meters
		ST_Transform(way,32616) AS geom
	FROM gta_line
	WHERE 
		highway IS NOT NULL AND 
		highway NOT IN (
			'cycleway','service','footway','pedestrian','path','steps',
			'motorway','motorway_link','trunk','trunk_link'
		)
""")
print 'starting to generate points'

# write the output
outfile = open('street-points.csv','w')
outfile.write('x,y\n')

for (line_hex,) in cursor:
	line = loadWKB(line_hex,hex=True)
	# for every 10m increment, there is a chance a point will be 
	# placed somewhere on this line 
	for i in range (0,int(math.ceil(line.length)),10):
		if random.random() < 0.2:
			point = line.interpolate(random.random()*line.length)
			outfile.write(str(point.x)+','+str(point.y)+'\n')
outfile.close()
