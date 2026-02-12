-- LFC Quotes Seed Data
-- Focus on City rivalry + iconic quotes

INSERT INTO quotes (quote_text, author, context, year, tags) VALUES
-- Klopp era
('This means more.', 'Jürgen Klopp', 'LFC identity campaign', 2019, ARRAY['identity', 'emotional', 'Klopp']),
('We are Liverpool. This means more.', 'Jürgen Klopp', 'Champions League Final 2019', 2019, ARRAY['Champions League', 'identity', 'Klopp']),
('I''m a very lucky man because I''m at a club where I can be myself.', 'Jürgen Klopp', 'Interview', 2020, ARRAY['Klopp', 'identity']),
('If you want to win, you have to be ready to fight.', 'Jürgen Klopp', 'Pre-match press conference', 2019, ARRAY['Klopp', 'mentality']),
('The difference between City and us? We have Anfield.', 'Jürgen Klopp', 'Title race 2019', 2019, ARRAY['City', 'Anfield', 'rivalry', 'Klopp']),

-- Legends
('A lot of football success is in the mind.', 'Bill Shankly', 'Interview', 1970, ARRAY['Shankly', 'mentality', 'legend']),
('The socialism I believe in is everyone working for each other.', 'Bill Shankly', 'Interview', 1973, ARRAY['Shankly', 'identity', 'legend']),
('Above all, I would like to be remembered as a man who was selfless.', 'Bill Shankly', 'Autobiography', 1976, ARRAY['Shankly', 'legend']),
('Liverpool was made for me and I was made for Liverpool.', 'Bill Shankly', 'On joining LFC', 1959, ARRAY['Shankly', 'identity', 'legend']),

-- Gerrard
('This does not fucking slip now.', 'Steven Gerrard', 'Chelsea match 2014 (before the slip)', 2014, ARRAY['Gerrard', 'City', 'title race', 'ironic']),
('I''ve been a Liverpool fan all my life and it''s something I''m very proud of.', 'Steven Gerrard', 'Interview', 2005, ARRAY['Gerrard', 'identity', 'legend']),
('We go again.', 'Steven Gerrard', 'Half-time team talk', 2014, ARRAY['Gerrard', 'mentality', 'iconic']),

-- Anfield specific
('When you walk through a storm, hold your head up high.', 'Gerry & The Pacemakers / Anfield', 'YNWA', 1963, ARRAY['YNWA', 'Anfield', 'anthem']),
('Anfield is not a stadium, it''s a religion.', 'Arrigo Sacchi', 'On Liverpool', 1990, ARRAY['Anfield', 'atmosphere', 'respect']),

-- City rivalry specific
('They can buy players, but they can''t buy history.', 'Anonymous Liverpool fan', 'Banner at Anfield', 2010, ARRAY['City', 'rivalry', 'history', 'oil money']),
('Money can''t buy you love. Or European Cups.', 'Liverpool fan banner', 'Champions League', 2018, ARRAY['City', 'rivalry', 'Champions League', 'banter']),

-- Recent era
('Mo Salah, Mo Salah, running down the wing...', 'LFC fans', 'Chant', 2018, ARRAY['Salah', 'chant', 'modern']),
('Virgil van Dijk, Virgil van Dijk, sitting in a tree...', 'LFC fans', 'Chant variation', 2019, ARRAY['Van Dijk', 'chant', 'modern']),

-- Respect for opponents
('Manchester City are an incredible team. That makes beating them even sweeter.', 'Jürgen Klopp', 'Post-match', 2020, ARRAY['City', 'rivalry', 'respect', 'Klopp']);
