-- Product source for the approved eight-table model; NOT EXECUTED.
-- Run as lumia_migrator only after the user's final structure/target confirmation.
-- Flyway owns the transaction. No automatic replacement or conflict skipping.
CREATE FUNCTION public.reject_common_pk_update()
RETURNS trigger
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = pg_catalog
AS $guard$
BEGIN
    IF OLD.id IS DISTINCT FROM NEW.id THEN
        RAISE EXCEPTION USING ERRCODE = 'LW001',
            MESSAGE = 'Common primary key cannot be changed.';
    END IF;
    RETURN NEW;
END;
$guard$;

REVOKE ALL ON FUNCTION public.reject_common_pk_update() FROM PUBLIC;

CREATE TABLE public.season (
    id BIGINT GENERATED ALWAYS AS IDENTITY CONSTRAINT pk_season PRIMARY KEY,
    season_number INTEGER CONSTRAINT nn_season_number NOT NULL,
    display_name TEXT CONSTRAINT nn_season_display_name NOT NULL,
    season_name TEXT,
    sort_order BIGINT CONSTRAINT nn_season_order NOT NULL,
    start_date DATE,
    end_date DATE,
    CONSTRAINT uq_season_number UNIQUE (season_number) NOT DEFERRABLE,
    CONSTRAINT ck_season_number CHECK (season_number >= 1),
    CONSTRAINT ck_season_display_name CHECK (btrim(display_name) <> ''),
    CONSTRAINT ck_season_actual_name CHECK (season_name IS NULL OR btrim(season_name) <> ''),
    CONSTRAINT ck_season_order CHECK (sort_order = season_number::bigint + 9),
    CONSTRAINT ck_season_dates CHECK (start_date IS NULL OR end_date IS NULL OR end_date >= start_date)
);
CREATE TRIGGER trg_season_reject_pk_update AFTER UPDATE ON public.season
FOR EACH ROW EXECUTE FUNCTION public.reject_common_pk_update();

CREATE TABLE public.region (
    id BIGINT GENERATED ALWAYS AS IDENTITY CONSTRAINT pk_region PRIMARY KEY,
    display_name TEXT COLLATE "C" CONSTRAINT nn_region_display_name NOT NULL,
    CONSTRAINT uq_region_display_name UNIQUE (display_name) NOT DEFERRABLE,
    CONSTRAINT ck_region_display_name CHECK (btrim(display_name) <> '')
);
CREATE TRIGGER trg_region_reject_pk_update AFTER UPDATE ON public.region
FOR EACH ROW EXECUTE FUNCTION public.reject_common_pk_update();

CREATE TABLE public.item_category (
    id BIGINT GENERATED ALWAYS AS IDENTITY CONSTRAINT pk_item_category PRIMARY KEY,
    name TEXT COLLATE "C" CONSTRAINT nn_item_category_name NOT NULL,
    parent_id BIGINT,
    CONSTRAINT uq_item_category_parent_name UNIQUE NULLS NOT DISTINCT (parent_id, name) NOT DEFERRABLE,
    CONSTRAINT ck_item_category_name CHECK (btrim(name) <> ''),
    CONSTRAINT ck_item_category_parent CHECK (parent_id IS NULL OR parent_id <> id),
    CONSTRAINT fk_item_category_parent FOREIGN KEY (parent_id) REFERENCES public.item_category (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE
);
CREATE TRIGGER trg_item_category_reject_pk_update AFTER UPDATE ON public.item_category
FOR EACH ROW EXECUTE FUNCTION public.reject_common_pk_update();

CREATE TABLE public.item_grade (
    id BIGINT GENERATED ALWAYS AS IDENTITY CONSTRAINT pk_item_grade PRIMARY KEY,
    name TEXT COLLATE "C" CONSTRAINT nn_item_grade_name NOT NULL,
    sort_order BIGINT CONSTRAINT nn_item_grade_order NOT NULL,
    CONSTRAINT uq_item_grade_name UNIQUE (name) NOT DEFERRABLE,
    CONSTRAINT uq_item_grade_order UNIQUE (sort_order) NOT DEFERRABLE,
    CONSTRAINT ck_item_grade_name CHECK (btrim(name) <> '')
);
CREATE TRIGGER trg_item_grade_reject_pk_update AFTER UPDATE ON public.item_grade
FOR EACH ROW EXECUTE FUNCTION public.reject_common_pk_update();

CREATE TABLE public.game_patch (
    id BIGINT GENERATED ALWAYS AS IDENTITY CONSTRAINT pk_game_patch PRIMARY KEY,
    season_id BIGINT CONSTRAINT nn_game_patch_season NOT NULL,
    major_no INTEGER CONSTRAINT nn_game_patch_major NOT NULL,
    minor_no INTEGER CONSTRAINT nn_game_patch_minor NOT NULL,
    version_name TEXT,
    sort_order BIGINT CONSTRAINT nn_game_patch_order NOT NULL,
    applied_at TIMESTAMPTZ(0),
    CONSTRAINT uq_game_patch_number UNIQUE (season_id, major_no, minor_no) NOT DEFERRABLE,
    CONSTRAINT uq_game_patch_order UNIQUE (sort_order) NOT DEFERRABLE,
    CONSTRAINT ck_game_patch_major CHECK (major_no BETWEEN 0 AND 99),
    CONSTRAINT ck_game_patch_minor CHECK (minor_no BETWEEN 0 AND 99),
    CONSTRAINT ck_game_patch_name CHECK (version_name IS NULL OR btrim(version_name) <> ''),
    CONSTRAINT fk_game_patch_season FOREIGN KEY (season_id) REFERENCES public.season (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE
);
CREATE TRIGGER trg_game_patch_reject_pk_update AFTER UPDATE ON public.game_patch
FOR EACH ROW EXECUTE FUNCTION public.reject_common_pk_update();

CREATE TABLE public.weapon_type (
    id BIGINT GENERATED ALWAYS AS IDENTITY CONSTRAINT pk_weapon_type PRIMARY KEY,
    name TEXT COLLATE "C" CONSTRAINT nn_weapon_type_name NOT NULL,
    category_id BIGINT CONSTRAINT nn_weapon_type_category NOT NULL,
    CONSTRAINT uq_weapon_type_name UNIQUE (name) NOT DEFERRABLE,
    CONSTRAINT uq_weapon_type_category UNIQUE (category_id) NOT DEFERRABLE,
    CONSTRAINT ck_weapon_type_name CHECK (btrim(name) <> ''),
    CONSTRAINT fk_weapon_type_category FOREIGN KEY (category_id) REFERENCES public.item_category (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE
);
CREATE TRIGGER trg_weapon_type_reject_pk_update AFTER UPDATE ON public.weapon_type
FOR EACH ROW EXECUTE FUNCTION public.reject_common_pk_update();

CREATE TABLE public.region_map_version (
    id BIGINT GENERATED ALWAYS AS IDENTITY CONSTRAINT pk_region_map_version PRIMARY KEY,
    from_game_patch_id BIGINT CONSTRAINT nn_region_map_start NOT NULL,
    CONSTRAINT uq_region_map_start UNIQUE (from_game_patch_id) NOT DEFERRABLE,
    CONSTRAINT fk_region_map_start FOREIGN KEY (from_game_patch_id) REFERENCES public.game_patch (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE
);
CREATE TRIGGER trg_region_map_version_reject_pk_update AFTER UPDATE ON public.region_map_version
FOR EACH ROW EXECUTE FUNCTION public.reject_common_pk_update();

CREATE TABLE public.region_map_member (
    id BIGINT GENERATED ALWAYS AS IDENTITY CONSTRAINT pk_region_map_member PRIMARY KEY,
    map_version_id BIGINT CONSTRAINT nn_region_map_member_map NOT NULL,
    region_id BIGINT CONSTRAINT nn_region_map_member_region NOT NULL,
    name TEXT COLLATE "C" CONSTRAINT nn_region_map_member_name NOT NULL,
    sort_order BIGINT CONSTRAINT nn_region_map_member_order NOT NULL,
    CONSTRAINT uq_region_map_member_region UNIQUE (map_version_id, region_id) NOT DEFERRABLE,
    CONSTRAINT uq_region_map_member_name UNIQUE (map_version_id, name) NOT DEFERRABLE,
    CONSTRAINT uq_region_map_member_order UNIQUE (map_version_id, sort_order) NOT DEFERRABLE,
    CONSTRAINT ck_region_map_member_name CHECK (btrim(name) <> ''),
    CONSTRAINT ck_region_map_member_order CHECK (sort_order >= 10 AND sort_order % 10 = 0),
    CONSTRAINT fk_region_map_member_map FOREIGN KEY (map_version_id) REFERENCES public.region_map_version (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE,
    CONSTRAINT fk_region_map_member_region FOREIGN KEY (region_id) REFERENCES public.region (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE
);
CREATE TRIGGER trg_region_map_member_reject_pk_update AFTER UPDATE ON public.region_map_member
FOR EACH ROW EXECUTE FUNCTION public.reject_common_pk_update();

-- No ownership/DDL/TRIGGER/TRUNCATE/grant option, blanket sequence privileges,
-- or default privileges are added.
GRANT SELECT, INSERT, UPDATE ON TABLE
    public.season, public.game_patch, public.region, public.item_category,
    public.item_grade, public.weapon_type, public.region_map_version TO lumia_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.region_map_member TO lumia_app;
