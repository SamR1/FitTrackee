# flake8: noqa

expected_en_feed_workout_cycling_user_1 = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>test's workouts feed</title><link>https://example.com/users/test</link><description>Latest public workouts on FitTrackee from test</description><atom:link href="https://example.com/users/test/workouts.rss" rel="self"/><language>en</language><lastBuildDate>Mon, 01 Jan 2018 00:00:00 +0000</lastBuildDate><item><title>Cycling (Sport) - {workout_title}</title><link>https://example.com/workouts/{workout_short_id}</link><description>&lt;p&gt;
&lt;strong&gt;Duration&lt;/strong&gt;: 1:00:00&lt;br /&gt;
&lt;strong&gt;Distance&lt;/strong&gt;: 10.0 km&lt;br /&gt;</description><pubDate>Mon, 01 Jan 2018 00:00:00 +0000</pubDate></item></channel></rss>"""

expected_en_feed_workout_cycling_user_1_with_map = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>test's workouts feed</title><link>https://example.com/users/test</link><description>Latest public workouts on FitTrackee from test</description><atom:link href="https://example.com/users/test/workouts.rss" rel="self"/><language>en</language><lastBuildDate>Mon, 01 Jan 2018 00:00:00 +0000</lastBuildDate><item><title>Cycling (Sport) - {workout_title}</title><link>https://example.com/workouts/{workout_short_id}</link><description>&lt;p&gt;&lt;img src="https://example.com/api/workouts/map/{workout_map_id}" alt="Workout map"&gt;&lt;br /&gt;
&lt;strong&gt;Duration&lt;/strong&gt;: 1:00:00&lt;br /&gt;
&lt;strong&gt;Distance&lt;/strong&gt;: 10.0 km&lt;br /&gt;</description><pubDate>Mon, 01 Jan 2018 00:00:00 +0000</pubDate></item></channel></rss>"""

expected_en_feed_workout_cycling_user_1_with_elevation = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>test's workouts feed</title><link>https://example.com/users/test</link><description>Latest public workouts on FitTrackee from test</description><atom:link href="https://example.com/users/test/workouts.rss" rel="self"/><language>en</language><lastBuildDate>Mon, 01 Jan 2018 00:00:00 +0000</lastBuildDate><item><title>Cycling (Sport) - {workout_title}</title><link>https://example.com/workouts/{workout_short_id}</link><description>&lt;p&gt;
&lt;strong&gt;Duration&lt;/strong&gt;: 1:00:00&lt;br /&gt;
&lt;strong&gt;Distance&lt;/strong&gt;: 10.0 km&lt;br /&gt;&lt;strong&gt;Min. altitude&lt;/strong&gt;: 236.0 m&lt;br /&gt;&lt;strong&gt;Max. altitude&lt;/strong&gt;: 260.0 m&lt;br /&gt;&lt;strong&gt;Ascent&lt;/strong&gt;: 26.0 m&lt;strong&gt;&lt;br /&gt;Descent&lt;/strong&gt;: 12.0 m&lt;br /&gt;</description><pubDate>Mon, 01 Jan 2018 00:00:00 +0000</pubDate></item></channel></rss>"""

expected_en_feed_workout_cycling_user_1_without_elevation = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>test's workouts feed</title><link>https://example.com/users/test</link><description>Latest public workouts on FitTrackee from test</description><atom:link href="https://example.com/users/test/workouts.rss" rel="self"/><language>en</language><lastBuildDate>Mon, 01 Jan 2018 00:00:00 +0000</lastBuildDate><item><title>Cycling (Sport) - {workout_title}</title><link>https://example.com/workouts/{workout_short_id}</link><description>&lt;p&gt;
&lt;strong&gt;Duration&lt;/strong&gt;: 1:00:00&lt;br /&gt;
&lt;strong&gt;Distance&lt;/strong&gt;: 10.0 km&lt;br /&gt;&lt;strong&gt;Ascent&lt;/strong&gt;: 26.0 m&lt;strong&gt;&lt;br /&gt;Descent&lt;/strong&gt;: 12.0 m&lt;br /&gt;</description><pubDate>Mon, 01 Jan 2018 00:00:00 +0000</pubDate></item></channel></rss>"""


expected_fr_feed_workout_cycling_user_1_with_map = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>Flux de séances de test</title><link>https://example.com/users/test</link><description>Dernières séances publiques de test sur FitTrackee</description><atom:link href="https://example.com/users/test/workouts.rss" rel="self"/><language>fr</language><lastBuildDate>Mon, 01 Jan 2018 00:00:00 +0000</lastBuildDate><item><title>Vélo (Sport) - {workout_title}</title><link>https://example.com/workouts/{workout_short_id}</link><description>&lt;p&gt;&lt;img src="https://example.com/api/workouts/map/{workout_map_id}" alt="Carte de la séance"&gt;&lt;br /&gt;
&lt;strong&gt;Durée&lt;/strong&gt;: 1:00:00&lt;br /&gt;
&lt;strong&gt;Distance&lt;/strong&gt;: 10.0 km&lt;br /&gt;</description><pubDate>Mon, 01 Jan 2018 00:00:00 +0000</pubDate></item></channel></rss>"""

expected_en_feed_workout_cycling_user_1_in_imperial_units = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>test's workouts feed</title><link>https://example.com/users/test</link><description>Latest public workouts on FitTrackee from test</description><atom:link href="https://example.com/users/test/workouts.rss" rel="self"/><language>en</language><lastBuildDate>Mon, 01 Jan 2018 00:00:00 +0000</lastBuildDate><item><title>Cycling (Sport) - {workout_title}</title><link>https://example.com/workouts/{workout_short_id}</link><description>&lt;p&gt;
&lt;strong&gt;Duration&lt;/strong&gt;: 1:00:00&lt;br /&gt;
&lt;strong&gt;Distance&lt;/strong&gt;: 6.214 mi&lt;br /&gt;</description><pubDate>Mon, 01 Jan 2018 00:00:00 +0000</pubDate></item></channel></rss>"""

expected_en_feed_workout_cycling_user_1_with_elevation_in_imperial_units = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>test's workouts feed</title><link>https://example.com/users/test</link><description>Latest public workouts on FitTrackee from test</description><atom:link href="https://example.com/users/test/workouts.rss" rel="self"/><language>en</language><lastBuildDate>Mon, 01 Jan 2018 00:00:00 +0000</lastBuildDate><item><title>Cycling (Sport) - {workout_title}</title><link>https://example.com/workouts/{workout_short_id}</link><description>&lt;p&gt;
&lt;strong&gt;Duration&lt;/strong&gt;: 1:00:00&lt;br /&gt;
&lt;strong&gt;Distance&lt;/strong&gt;: 6.214 mi&lt;br /&gt;&lt;strong&gt;Min. altitude&lt;/strong&gt;: 774.28 ft&lt;br /&gt;&lt;strong&gt;Max. altitude&lt;/strong&gt;: 853.02 ft&lt;br /&gt;&lt;strong&gt;Ascent&lt;/strong&gt;: 85.3 ft&lt;strong&gt;&lt;br /&gt;Descent&lt;/strong&gt;: 39.37 ft&lt;br /&gt;</description><pubDate>Mon, 01 Jan 2018 00:00:00 +0000</pubDate></item></channel></rss>"""


expected_en_empty_feed = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>{username}'s workouts feed</title><link>https://example.com/users/{username}</link><description>Latest public workouts on FitTrackee from {username}</description><atom:link href="https://example.com/users/{username}/workouts.rss" rel="self"/><language>en</language><lastBuildDate>{last_date}</lastBuildDate></channel></rss>"""


expected_en_feed_user_1_workouts = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>test's workouts feed</title><link>https://example.com/users/test</link><description>Latest public workouts on FitTrackee from test</description><atom:link href="https://example.com/users/test/workouts.rss" rel="self"/><language>en</language><lastBuildDate>Wed, 09 May 2018 00:00:00 +0000</lastBuildDate><item><title>Cycling (Sport) - Workout 7 of 7</title><link>https://example.com/workouts/{workout_1_short_id}</link><description>&lt;p&gt;
&lt;strong&gt;Duration&lt;/strong&gt;: 0:50:00&lt;br /&gt;
&lt;strong&gt;Distance&lt;/strong&gt;: 10.0 km&lt;br /&gt;</description><pubDate>Wed, 09 May 2018 00:00:00 +0000</pubDate></item><item><title>Cycling (Sport) - Workout 5 of 7</title><link>https://example.com/workouts/{workout_2_short_id}</link><description>&lt;p&gt;
&lt;strong&gt;Duration&lt;/strong&gt;: 0:16:40&lt;br /&gt;
&lt;strong&gt;Distance&lt;/strong&gt;: 10.0 km&lt;br /&gt;&lt;strong&gt;Ascent&lt;/strong&gt;: 100.0 m&lt;strong&gt;&lt;br /&gt;Descent&lt;/strong&gt;: 200.0 m&lt;br /&gt;</description><pubDate>Fri, 23 Feb 2018 00:00:00 +0000</pubDate></item></channel></rss>"""
