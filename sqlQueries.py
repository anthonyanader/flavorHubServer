queries = {
'f':
'''select "user".username, restaurant.name, cast(round(avg(price)) as INT) as price_Rating, cast(round(avg(mood)) as INT) as mood_Rating, cast(round(avg(staff)) as INT) as staff_Rating, cast(round(avg(food)) as INT) as food_Rating
from rating, "user", restaurant
where "user".id = "userId" and restaurant.id = rating."restaurantId"
group by("user".username, restaurant.name)
order by ("user".username)
limit 20''',

'g':
'''select restaurant.name as restaurant_name, cuisine_type.name as cuisine_name, location."phoneNumber" as phone_number
from rating, restaurant, location, cuisine_type
where (rating.date > '20150131' or rating.date < '20150101')
and rating."restaurantId" = restaurant.id
and cuisine_type."restaurantId" = restaurant.id
and location."restaurantId" = restaurant.id
limit 20''',

'h':
'''select distinct(restaurant.name) as restaurant_name
from rating, restaurant
where rating."restaurantId" = restaurant.id
and ((staff <= (select min(price)
           	from "user", rating
            where "user".username='imfil'
            and rating."userId" = "user".id))
            or
     		(staff <= (select min(food)
           	from "user", rating
            where "user".username='imfil'
            and rating."userId" = "user".id))
    		or
     		(staff <= (select min(mood)
           	from "user", rating
            where "user".username='imfil'
            and rating."userId" = "user".id))
    		or
     		(staff <= (select min(staff)
           	from "user", rating
            where "user".username='imfil'
            and rating."userId" = "user".id)))
limit 20''',

'i':
'''select "user".username, restaurant.name as restaurant_name, max(rating.food) as food
from cuisine_type, restaurant, rating, "user"
where cuisine_type.name = 'Burger'
and cuisine_type."restaurantId" = restaurant.id
and rating."restaurantId" = restaurant.id
and "user".id = rating."userId"
group by "user".username, restaurant.name, food
having food = (select max(rating.food) as food
				from cuisine_type, restaurant, rating
				where cuisine_type.name = 'Burger'
				and cuisine_type."restaurantId" = restaurant.id
				and rating."restaurantId" = restaurant.id
                )
order by restaurant.name
limit 20''',

'j':
'''select restaurant.name as restaurant_name, max(rating.food) as food, max(rating.price) as price, max(rating.mood) as mood, max(rating.staff) as staff
from cuisine_type, restaurant, rating
where cuisine_type.name = 'Burger'
and cuisine_type."restaurantId" = restaurant.id
and rating."restaurantId" = restaurant.id
group by restaurant.name, food, price, mood, staff
having food = (select max(rating.food) as food
				from cuisine_type, restaurant, rating
				where cuisine_type.name = 'Burger'
				and cuisine_type."restaurantId" = restaurant.id
				and rating."restaurantId" = restaurant.id
                )
       and price = (select max(rating.price) as price
				from cuisine_type, restaurant, rating
				where cuisine_type.name = 'Burger'
				and cuisine_type."restaurantId" = restaurant.id
				and rating."restaurantId" = restaurant.id
                )
       and staff = (select max(rating.staff) as staff
				from cuisine_type, restaurant, rating
				where cuisine_type.name = 'Burger'
				and cuisine_type."restaurantId" = restaurant.id
				and rating."restaurantId" = restaurant.id
                )
       and mood = (select max(rating.mood) as mood
				from cuisine_type, restaurant, rating
				where cuisine_type.name = 'Burger'
				and cuisine_type."restaurantId" = restaurant.id
				and rating."restaurantId" = restaurant.id
                )
order by restaurant.name
limit 20''',

'k':
'''SELECT U.username, U.rating, R.name, R8.date
FROM "user" U, restaurant R, rating R8
WHERE U.id IN (SELECT U1.id
                   FROM "user" U1
                   group by U1.id
                   HAVING (SELECT AVG(Rate.mood + Rate.food)
                           FROM rating Rate
                           WHERE Rate."userId" = U1.id) >= ALL(SELECT AVG(Rate1.mood + Rate1.food)
                                                                 FROM rating Rate1, "user" U2
                                                                 WHERE Rate1.id = U2.id GROUP BY U2.id))
AND R8."userId" = U.id AND R8."restaurantId" = R.id''',


'l':
'''SELECT U.fname as first_name, U.rating, R.name as restaurant_name, R8.date
FROM "user" U, restaurant R, rating R8
WHERE U.id IN (SELECT U1.id
                   FROM "user" U1
                   WHERE (SELECT AVG(mood)
                          FROM rating Rate
                          WHERE Rate."userId" = U1.id) >= ALL(SELECT AVG(mood)
                                                                FROM rating Rate
                                                                GROUP BY Rate."userId")
		OR (SELECT AVG(food)
            FROM rating Rate
            WHERE Rate."userId" = U1.id) >= ALL(SELECT AVG(food)
                                                  FROM rating Rate
                                                  GROUP BY Rate."userId"))
		AND R8."userId" = U.id AND R8."restaurantId" = R.id
limit 20''',

'm':
'''SELECT U.fname as first_name, U.rating, R8.comment
FROM rating R8, "user" U
WHERE  U.id IN (SELECT U1.id
                    FROM "user" U1
                    WHERE (SELECT COUNT(*)
                           FROM rating Rate
                           WHERE Rate."userId" = U1.id
                           AND Rate."restaurantId" IN (SELECT R.id
                                                     FROM restaurant R
                                                     WHERE R.name ='Benoit')) >=  All(SELECT COUNT(*)
                                                                                 FROM rating Rate1
                                                                                 WHERE Rate1."restaurantId" IN (SELECT R.id
                                                                                                              FROM restaurant R
                                                                                                              WHERE R.name ='Benoit')
                                                                                 GROUP BY Rate1."userId"))
      AND R8."userId" = U.id
      AND R8."restaurantId" IN (SELECT R.id
                              FROM restaurant R
                              WHERE R.name ='Benoit')
limit 20''',

'n':
'''SELECT U.fname, U.email
FROM "user" U
WHERE U.id IN (SELECT R8."userId"
                   FROM rating R8
                   WHERE (R8.price + R8.food + R8.mood + R8.staff)
                   < ANY(SELECT (Rate.price + Rate.mood + Rate.food + Rate.staff)
                         FROM rating Rate
                         WHERE Rate."userId" IN (SELECT U1.id
                                               FROM "user" U1
                                               WHERE U1.fname = 'James')))
limit 20'''

}
