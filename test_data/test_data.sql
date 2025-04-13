BEGIN;

-- Справочники
INSERT INTO family_status(name) VALUES ('zamuzhem');
INSERT INTO political_party(name) VALUES ('COMMUNIZM');
INSERT INTO religion(name) VALUES ('god');
INSERT INTO social_class(name) VALUES ('molodec');
INSERT INTO nationality(name) VALUES ('russki');
INSERT INTO education(name) VALUES ('obrazovan');
INSERT INTO occupation(name) VALUES ('rabotnik');
INSERT INTO card(name) VALUES ('xleb');

-- Типы заметок
INSERT INTO note_type(name) VALUES ('real');
INSERT INTO note_type(name) VALUES ('unreal');

-- Типы точек
INSERT INTO point_type(name, has_fixed_coordinates, has_address) VALUES ('point type 1', TRUE, TRUE);
INSERT INTO point_type(name, has_fixed_coordinates, has_address) VALUES ('point type 2', FALSE, FALSE);

-- Подтипы точек (исправлено согласно моделям)
INSERT INTO point_subtype(name, point_type_id) VALUES ('point subtype', 1);
INSERT INTO point_subsubtype(name, point_subtype_id) VALUES ('point subsubtype', 1);

-- Районы
INSERT INTO rayon(name) VALUES ('central');

-- Временность
INSERT INTO temporality(name) VALUES ('direct');
INSERT INTO temporality(name) VALUES ('indirect');

-- Теги
INSERT INTO tag(name) VALUES ('important');
INSERT INTO tag(name) VALUES ('historical');

-- Автор
INSERT INTO author(
    first_name, middle_name, last_name,
    sex, birth_date, family_status_id,
    has_children, biography
) VALUES (
    'Ivan', 'Ivanovich', 'Ivanov',
    'M', '1910-01-01', 1,
    TRUE, 'Test biography'
);

-- Дневник
INSERT INTO diary(
    author_id, started_at, finished_at, source
) VALUES (
    1, '1941-01-01', '1945-01-01', 'Test sources'
);

-- Точка
INSERT INTO point(
    name, rayon_id, street, building,
    point_type_id, point_subtype_id, point_subsubtype_id,
    description
) VALUES (
    'Test point', 1, 'Main street', '1',
    1, 1, 1,
    'Test description'
);

-- Координаты точки (исправлено на раздельные latitude/longitude)
INSERT INTO point_coordinates(point_id, latitude, longitude)
VALUES (1, 59.934280, 30.335098);

-- Заметка
INSERT INTO note(
    diary_id, note_type_id, temporality_id,
    created_at, citation, source
) VALUES (
    1, 1, 1,
    '1942-01-01', 'Test citation', 'Test source'
);

-- Связи многие-ко-многим
INSERT INTO note_to_point(note_id, point_id, description)
VALUES (1, 1, 'Test connection');

INSERT INTO note_to_tag(note_id, tag_id) VALUES (1, 1);

INSERT INTO author_to_point(
    author_id, point_id, from_date, to_date, description
) VALUES (
    1, 1, '1941-01-01', '1945-01-01', 'Test author-point connection'
);

-- Связи автора с другими сущностями
INSERT INTO author_to_political_party(author_id, political_party_id) VALUES (1, 1);
INSERT INTO author_to_religion(author_id, religion_id) VALUES (1, 1);
INSERT INTO author_to_social_class(author_id, social_class_id) VALUES (1, 1);
INSERT INTO author_to_nationality(author_id, nationality_id) VALUES (1, 1);
INSERT INTO author_to_education(author_id, education_id) VALUES (1, 1);
INSERT INTO author_to_occupation(author_id, occupation_id) VALUES (1, 1);
INSERT INTO author_to_card(author_id, card_id) VALUES (1, 1);

COMMIT;