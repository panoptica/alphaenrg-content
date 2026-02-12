-- LFC vs Manchester City Stats Seed Data

INSERT INTO stats (stat_type, opponent, stat_data) VALUES
-- Head to head all time
('head_to_head', 'Manchester City', '{
    "total_matches": 195,
    "lfc_wins": 92,
    "city_wins": 58,
    "draws": 45,
    "lfc_goals": 324,
    "city_goals": 253,
    "last_updated": "2025-02-05"
}'::jsonb),

-- Anfield record
('anfield_record', 'Manchester City', '{
    "total_matches": 97,
    "lfc_wins": 54,
    "city_wins": 16,
    "draws": 27,
    "lfc_goals": 178,
    "city_goals": 98,
    "city_last_win": "2021-02-07",
    "note": "City have won just twice at Anfield in the Premier League era"
}'::jsonb),

-- Notable results
('notable_results', 'Manchester City', '{
    "matches": [
        {"date": "2019-11-10", "score": "3-1", "venue": "Anfield", "competition": "Premier League", "note": "Title race statement win", "scorers": ["Fabinho", "Salah", "Mane"]},
        {"date": "2018-01-14", "score": "4-3", "venue": "Anfield", "competition": "Premier League", "note": "Ended City''s unbeaten run", "scorers": ["Oxlade-Chamberlain", "Firmino", "Mane", "Salah"]},
        {"date": "2018-04-04", "score": "3-0", "venue": "Anfield", "competition": "Champions League QF", "note": "First leg demolition", "scorers": ["Salah", "Oxlade-Chamberlain", "Mane"]},
        {"date": "2014-04-13", "score": "3-2", "venue": "Anfield", "competition": "Premier League", "note": "Gerrard slip match", "scorers": ["Sterling", "Skrtel", "Coutinho"]},
        {"date": "2013-12-26", "score": "2-1", "venue": "Etihad", "competition": "Premier League", "note": "Boxing Day shock", "scorers": ["Coutinho", "Henderson"]}
    ]
}'::jsonb),

-- Premier League era head to head
('premier_league_h2h', 'Manchester City', '{
    "total_matches": 62,
    "lfc_wins": 23,
    "city_wins": 22,
    "draws": 17,
    "note": "Incredibly tight in modern era"
}'::jsonb),

-- Recent form (last 10 meetings)
('recent_form', 'Manchester City', '{
    "matches": 10,
    "lfc_wins": 3,
    "city_wins": 4,
    "draws": 3,
    "note": "Last 10 competitive meetings"
}'::jsonb),

-- Guardiola at Anfield
('guardiola_anfield', 'Manchester City', '{
    "total_visits": 8,
    "wins": 1,
    "draws": 2,
    "losses": 5,
    "note": "Anfield remains Pep''s bogey ground"
}'::jsonb);
