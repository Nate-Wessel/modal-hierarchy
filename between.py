import psycopg2, requests, json, random, math

num_pairs = int(raw_input('Number of OD pairs to route: '))
min_dist = int(raw_input('Min straight-line distance (m): '))
max_dist = int(raw_input('Max straight-line distance (m): '))

# connect to the census data DB
conn_string = ("host='localhost' dbname='osm' user='nate' password=''")
misc_conn = psycopg2.connect(conn_string)
misc_cursor = misc_conn.cursor()

# OSRM API parameters
options = {
	'annotations':'true',
	'overview':'false',
	'steps':'false',
	'alternatives':'false'
}

# get a list of origin and destination points
print "Getting OD's"
misc_cursor.execute("""
	SELECT 
		ST_X(geom),ST_Y(geom),
		x,y
	FROM street_points_cincy
""")
peeps = misc_cursor.fetchall()
print 'Starting...'

# dict of edge counts keyed by osm id pairs, ascending order
pairs = {}

count = 0
# draw random OD pairs until reaching desired number
while count < num_pairs:
	Olon,Olat,Ox,Oy = random.choice(peeps)
	Dlon,Dlat,Dx,Dy = random.choice(peeps)
	# check that the straight-line distance is less than the max
	straight_line_dist = math.sqrt( abs(Ox-Dx)**2 + abs(Oy-Dy)**2 )
	if straight_line_dist > max_dist:
		continue
	# craft and send the request
	response = requests.get(
		'http://localhost:5000/route/v1/car/'+str(Olon)+','+str(Olat)+';'+str(Dlon)+','+str(Dlat),
		params=options,
		timeout=10 # actually takes ~5ms
	)
	# parse the output
	j = json.loads(response.text)
	if j['code'] != 'Ok':
		continue
	# check that the trip isn't too long (e.g. opposite side of a river)	
	# or too short
	network_distance = j['routes'][0]['distance']
	if not min_dist < network_distance < max_dist:
		continue 
	# get the nodelist
	nodes = j['routes'][0]['legs'][0]['annotation']['nodes']

	# iterate over internode segments
	n1 = nodes[0]
	for i in range(1,len(nodes)):
		n2 = nodes[i]
		# order the nodes consistently
		if n1 < n2:
			key = str(n1)+'-'+str(n2)
		else: 
			key = str(n2)+'-'+str(n1)
		# increment the count
		if key not in pairs:
			pairs[key] = 1
		else:
			pairs[key] += 1
		# set for next iteration
		n1 = n2

	count += 1
	if count % 100 == 0:
		print num_pairs - count, 'paths remaining'

# write the output
outfile = open('nodepairs.csv','w')
outfile.write('n1,n2,count\n')
for key,value in pairs.items():
	n1,n2 = key.split('-')
	outfile.write(n1+','+n2+','+str(value)+'\n')
outfile.close()



