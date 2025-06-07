
-- 2. ¿Cuáles son las clases de peso con mayor cantidad de luchadores en la UFC?
SELECT wc.class,
       COUNT(DISTINCT fgtr.id) AS count_fighters
FROM fights f
JOIN fighters fgtr 
    ON f.fighter_1_id = fgtr.id OR f.fighter_2_id = fgtr.id
JOIN weight_classes wc ON f.weight_class_id = wc.id
GROUP BY wc.class 
ORDER BY count_fighters DESC;
-- Grafico de pastel con dropdown para interaccion


-- 3. ¿Cuál es la relación entre la edad de un luchador y sus victorias en UFC?
SELECT fgtr.fighter_name,
       YEAR(e.event_date) AS fight_year,
       TIMESTAMPDIFF(YEAR, fgtr.date_of_birth, e.event_date) AS age,
       SUM(CASE 
               WHEN (fs.fighter_1_fight_conclusion = 'W' AND f.fighter_1_id = fgtr.id) OR
                    (fs.fighter_2_fight_conclusion = 'W' AND f.fighter_2_id = fgtr.id) 
               THEN 1 
               ELSE 0 
           END) AS wins_at_year
FROM fighters fgtr
JOIN fights f ON f.fighter_1_id = fgtr.id OR f.fighter_2_id = fgtr.id
JOIN events e ON f.event_id = e.id
JOIN fight_stats fs ON f.id = fs.fight_id
WHERE fgtr.date_of_birth IS NOT NULL AND fgtr.wins IS NOT NULL
GROUP BY fgtr.fighter_name, YEAR(e.event_date)
ORDER BY fgtr.fighter_name DESC, fight_year DESC;
-- Scatter plot con slide para edad y victorias

-- 4. ¿Cuál es la distribución de victorias y derrotas en peleas según las clases de peso?
-- no sense
SELECT wc.class,
       -- Count victories for fighter 1 (when fighter_1 wins)
       SUM(CASE WHEN f1.fighter_1_fight_conclusion = 'W' THEN 1 ELSE 0 END) +
       -- Count losses for fighter 2 (when fighter_2 loses)
       SUM(CASE WHEN f1.fighter_2_fight_conclusion = 'F' THEN 1 ELSE 0 END) AS wins,
       
       -- Count losses for fighter 1 (when fighter_1 loses)
       SUM(CASE WHEN f1.fighter_1_fight_conclusion = 'F' THEN 1 ELSE 0 END) +
       -- Count victories for fighter 2 (when fighter_2 wins)
       SUM(CASE WHEN f1.fighter_2_fight_conclusion = 'W' THEN 1 ELSE 0 END) AS losses
FROM fights f
JOIN weight_classes wc ON f.weight_class_id = wc.id
JOIN fight_stats f1 ON f.id = f1.fight_id
WHERE f1.fighter_1_fight_conclusion IN ('W', 'F')
   OR f1.fighter_2_fight_conclusion IN ('W', 'F')
GROUP BY wc.class
ORDER BY wins DESC;
-- Stacked bar con filtro por clase de peso (dropdown)

-- ¿Cómo influye la altura y el peso de un luchador en su rendimiento (victorias y derrotas)?
SELECT
    fgtr.fighter_name,
    fgtr.height,
    fgtr.weight,
    fgtr.wins,
    fgtr.losses,
    fgtr.draws,
    (fgtr.wins + fgtr.losses + fgtr.draws) AS total_fights
FROM fighters fgtr
WHERE fgtr.height IS NOT NULL
  AND fgtr.weight IS NOT NULL;

-- Scatter plot o Bubble chart con slides para peso y altura


-- ¿Cuál es la relación entre el número de peleas de un luchador y su probabilidad de ganar?
SELECT 
    fgtr.id,
    fgtr.fighter_name,
    fgtr.wins,
    fgtr.losses,
    -- Calculate the total number of fights
    (fgtr.wins + fgtr.losses + fgtr.draws) AS total_fights,
    -- Calculate the win ratio (wins / total_fights)
    IF(fgtr.wins + fgtr.losses > 0, fgtr.wins / (fgtr.wins + fgtr.losses), 0) AS win_probability
FROM fighters fgtr
WHERE fgtr.wins + fgtr.losses + fgtr.draws > 0 -- We filter out fighters who haven't fought yet
ORDER BY win_probability DESC;
-- Scatter plot con linea de regresion con filtro de total de peleas


-- 7. ¿Cuál es la frecuencia de ciertos métodos de victoria (KO, sumisión, decisión) en función de las clases de peso?
SELECT 
    wc.class, 
    m.method,
    COUNT(f.id) AS fight_count
FROM fights f
JOIN weight_classes wc ON f.weight_class_id = wc.id
JOIN methods m ON f.method_id = m.id
GROUP BY wc.class, m.method
ORDER BY wc.class, fight_count DESC;
-- Stacked bar chart con dropdown para seleccionar metodo de victoria


SELECT 
    wc.class, 
    -- Aquí contamos las victorias por cada tipo de método de victoria
    SUM(CASE WHEN m.method = 'U-DEC' THEN 1 ELSE 0 END) AS 'U-DEC',
    SUM(CASE WHEN m.method = 'SUB' THEN 1 ELSE 0 END) AS 'SUB',
    SUM(CASE WHEN m.method = 'KO/TKO' THEN 1 ELSE 0 END) AS 'KO/TKO',
    SUM(CASE WHEN m.method = 'S-DEC' THEN 1 ELSE 0 END) AS 'S-DEC',
    SUM(CASE WHEN m.method = 'M-DEC' THEN 1 ELSE 0 END) AS 'M-DEC',
    SUM(CASE WHEN m.method = 'CNC' THEN 1 ELSE 0 END) AS 'CNC',
    SUM(CASE WHEN m.method = 'DQ' THEN 1 ELSE 0 END) AS 'DQ',
    SUM(CASE WHEN m.method = 'Overturned' THEN 1 ELSE 0 END) AS 'Overturned',
    SUM(CASE WHEN m.method = 'Other' THEN 1 ELSE 0 END) AS 'Other'
FROM fights f
JOIN weight_classes wc ON f.weight_class_id = wc.id
JOIN methods m ON f.method_id = m.id
GROUP BY wc.class
ORDER BY wc.class;



-- ¿Cuál es la frecuencia de ciertos métodos de victoria (KO, sumisión, decisión) en función de las clases de peso?
SELECT 
    m.method, 
    -- Contamos las victorias (W) para cada tipo de método
    SUM(CASE WHEN f1.fighter_1_fight_conclusion = 'W' THEN 1 ELSE 0 END) + 
    SUM(CASE WHEN f1.fighter_2_fight_conclusion = 'W' THEN 1 ELSE 0 END) AS W,
    
    -- Contamos las derrotas (L) para cada tipo de método
    SUM(CASE WHEN f1.fighter_1_fight_conclusion = 'L' THEN 1 ELSE 0 END) + 
    SUM(CASE WHEN f1.fighter_2_fight_conclusion = 'L' THEN 1 ELSE 0 END) AS L,
    
    -- Contamos los empates (D) para cada tipo de método
    SUM(CASE WHEN f1.fighter_1_fight_conclusion = 'D' THEN 1 ELSE 0 END) + 
    SUM(CASE WHEN f1.fighter_2_fight_conclusion = 'D' THEN 1 ELSE 0 END) AS D,
    
    -- Contamos las peleas sin decisión (NC) para cada tipo de método
    SUM(CASE WHEN f1.fighter_1_fight_conclusion = 'NC' THEN 1 ELSE 0 END) + 
    SUM(CASE WHEN f1.fighter_2_fight_conclusion = 'NC' THEN 1 ELSE 0 END) AS NC
FROM fights f
JOIN fight_stats f1 ON f.id = f1.fight_id
JOIN methods m ON f.method_id = m.id
GROUP BY m.method
ORDER BY m.method;
-- Stacked bar con dropdown metodo de victoria



-- ¿Cuáles son los países con más eventos de UFC organizados?
-- needs to fix c.state column, should be c.country
SELECT 
    c.state,        -- País donde se organiza el evento
    COUNT(e.id) AS event_count   -- Número de eventos en ese país
FROM events e
JOIN countries c ON e.country_id = c.id
GROUP BY c.state  -- Agrupamos por país
ORDER BY event_count DESC;  -- Ordenamos por la cantidad de eventos
-- Bar chart filtrar por pais

-- Luchas por ano
SELECT 
	YEAR(e.event_date) as year,
    COUNT(f.id) AS fight_count
FROM fights f JOIN events e ON e.id = f.event_id
GROUP BY YEAR(e.event_date) ORDER BY YEAR(e.event_date) DESC;
-- bar chart filtro por ano
-- Porcentaje de conclusiones para cada luchador, cual es el luchador que gana mas por U-DEC, Take Down