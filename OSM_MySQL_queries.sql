#Loading of the CSV FILES into MYSQL database
###########################################################
LOAD DATA INFILE 'nodes.csv' INTO TABLE nodes
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES;

LOAD DATA INFILE 'nodes_tags.csv' INTO TABLE nodes_tags
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES;

LOAD DATA INFILE 'ways.csv' INTO TABLE ways
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES;

LOAD DATA INFILE 'ways_nodes.csv' INTO TABLE ways_nodes
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES;

LOAD DATA INFILE 'ways_tags.csv' INTO TABLE ways_tags
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES;

###########################################################



QUERIES USED
#############################################################
#Number of unique users 
SELECT COUNT(DISTINCT user) FROM 
(SELECT user FROM nodes UNION SELECT user FROM ways) AS sub;

#Number of nodes
select count(*) from nodes;

#Number of ways
select count(*) from ways; 

#Top 10 amenities with count in the city
SELECT COUNT(value) AS cnt, value 
FROM 
(SELECT value FROM nodes_tags
WHERE `key` = 'amenity'
 UNION ALL
SELECT value FROM ways_tags
WHERE `key` = 'amenity') as tags_amenity
GROUP BY value
ORDER BY cnt DESC
LIMIT 10;

#Top 10 cuisines with count in the city
SELECT COUNT(value) AS cnt, value 
FROM 
(SELECT value FROM nodes_tags
WHERE `key` = 'cuisine'
 UNION ALL
SELECT value FROM ways_tags
WHERE `key` = 'cuisine') as tags_cuisine
GROUP BY value
ORDER BY cnt DESC
LIMIT 10;

#Top 10 contributing users
SELECT user, COUNT(user) cnt FROM
(SELECT user from nodes UNION ALL
SELECT user FROM ways) sub
GROUP BY user
ORDER BY cnt DESC
LIMIT 10;

#Most widely seen postcodes
SELECT tags.value, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags 
	  UNION ALL 
      SELECT * FROM ways_tags) tags
WHERE tags.key='postcode'
GROUP BY tags.value
ORDER BY count DESC
LIMIT 5;

#Max speeds in bangalore
SELECT tags.value, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags 
	  UNION ALL 
      SELECT * FROM ways_tags) tags
WHERE tags.key='maxspeed'
GROUP BY tags.value
ORDER BY tags.value DESC
LIMIT 4;

#Most widely seen sources
SELECT tags.value, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags 
	  UNION ALL 
      SELECT * FROM ways_tags) tags
WHERE tags.key='source'
GROUP BY tags.value
ORDER BY count DESC
LIMIT 5;


#Most widely seen editors
SELECT tags.value, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags 
	  UNION ALL 
      SELECT * FROM ways_tags) tags
WHERE tags.key='created_by'
GROUP BY tags.value
ORDER BY count DESC;

#finding 1 edit users
select COUNT(user)
FROM
(SELECT user, COUNT(user) cnt FROM
(SELECT user from nodes UNION ALL
SELECT user FROM ways) sub
GROUP BY user
HAVING cnt = 1
ORDER BY cnt DESC) sub1;


#sum of all entries by users 
SELECT sum(cnt) 
FROM 
(SELECT user, COUNT(user) cnt FROM
(SELECT user from nodes UNION ALL
SELECT user FROM ways) sub
GROUP BY user
ORDER BY cnt DESC) sub1;
#3549690

#sum of TOP 10 contributors
SELECT sum(cnt) 
FROM 
(SELECT user, COUNT(user) cnt FROM
(SELECT user from nodes UNION ALL
SELECT user FROM ways) sub
GROUP BY user
ORDER BY cnt DESC LIMIT 10) sub1;
#1021777

#sum of TOP 20 contributors
SELECT sum(cnt) 
FROM 
(SELECT user, COUNT(user) cnt FROM
(SELECT user from nodes UNION ALL
SELECT user FROM ways) sub
GROUP BY user
ORDER BY cnt DESC LIMIT 20) sub1;

