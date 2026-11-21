-- Product migration for the first six item-storage tables.
-- Apply only after the complete structure and the execution target have been confirmed.
-- Flyway owns the transaction. No existing product object is replaced.

CREATE TABLE public.item (
    id BIGINT GENERATED ALWAYS AS IDENTITY CONSTRAINT pk_item PRIMARY KEY,
    searchable BOOLEAN CONSTRAINT nn_item_searchable NOT NULL DEFAULT TRUE
);

-- Required text checks use the Unicode White_Space code points, as does the service.
CREATE TABLE public.item_version (
    id BIGINT GENERATED ALWAYS AS IDENTITY CONSTRAINT pk_item_version PRIMARY KEY,
    item_id BIGINT CONSTRAINT nn_item_version_item NOT NULL,
    from_game_patch_id BIGINT CONSTRAINT nn_item_version_patch NOT NULL,
    category_id BIGINT CONSTRAINT nn_item_version_category NOT NULL,
    name TEXT CONSTRAINT nn_item_version_name NOT NULL,
    image_path TEXT,
    is_deleted BOOLEAN CONSTRAINT nn_item_version_deleted NOT NULL DEFAULT FALSE,
    stat_json JSONB CONSTRAINT nn_item_version_stat_json NOT NULL DEFAULT '[]'::jsonb,
    CONSTRAINT uq_item_version_item_patch UNIQUE (item_id, from_game_patch_id) NOT DEFERRABLE,
    CONSTRAINT uq_item_version_owner_identity UNIQUE (item_id, id) NOT DEFERRABLE,
    CONSTRAINT uq_item_version_id_patch UNIQUE (id, from_game_patch_id) NOT DEFERRABLE,
    CONSTRAINT ck_item_version_name CHECK (
        btrim(name, U&'\0009\000A\000B\000C\000D\0020\0085\00A0\1680\2000\2001\2002\2003\2004\2005\2006\2007\2008\2009\200A\2028\2029\202F\205F\3000') <> ''
    ),
    CONSTRAINT ck_item_version_stat_json CHECK (jsonb_typeof(stat_json) = 'array'),
    CONSTRAINT fk_item_version_item FOREIGN KEY (item_id) REFERENCES public.item (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE,
    CONSTRAINT fk_item_version_patch FOREIGN KEY (from_game_patch_id) REFERENCES public.game_patch (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE,
    CONSTRAINT fk_item_version_category FOREIGN KEY (category_id) REFERENCES public.item_category (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE
);

CREATE TABLE public.stat_type (
    id BIGINT GENERATED ALWAYS AS IDENTITY CONSTRAINT pk_stat_type PRIMARY KEY,
    name TEXT COLLATE "C" CONSTRAINT nn_stat_type_name NOT NULL,
    sort_order BIGINT CONSTRAINT nn_stat_type_order NOT NULL,
    CONSTRAINT uq_stat_type_name UNIQUE (name) NOT DEFERRABLE,
    CONSTRAINT uq_stat_type_order UNIQUE (sort_order) NOT DEFERRABLE,
    CONSTRAINT ck_stat_type_name CHECK (
        btrim(name, U&'\0009\000A\000B\000C\000D\0020\0085\00A0\1680\2000\2001\2002\2003\2004\2005\2006\2007\2008\2009\200A\2028\2029\202F\205F\3000') <> ''
    )
);

CREATE TABLE public.item_skill_definition (
    id BIGINT GENERATED ALWAYS AS IDENTITY CONSTRAINT pk_item_skill_definition PRIMARY KEY
);

CREATE TABLE public.item_skill_definition_version (
    id BIGINT GENERATED ALWAYS AS IDENTITY CONSTRAINT pk_item_skill_definition_version PRIMARY KEY,
    item_skill_definition_id BIGINT CONSTRAINT nn_item_skill_definition_version_owner NOT NULL,
    from_game_patch_id BIGINT CONSTRAINT nn_item_skill_definition_version_patch NOT NULL,
    internal_name TEXT CONSTRAINT nn_item_skill_definition_version_name NOT NULL,
    description TEXT CONSTRAINT nn_item_skill_definition_version_description NOT NULL,
    CONSTRAINT uq_item_skill_definition_version_owner_id
        UNIQUE (item_skill_definition_id, id) NOT DEFERRABLE,
    CONSTRAINT uq_item_skill_definition_version_start_patch
        UNIQUE (item_skill_definition_id, from_game_patch_id) NOT DEFERRABLE,
    CONSTRAINT ck_item_skill_definition_version_name CHECK (
        btrim(internal_name, U&'\0009\000A\000B\000C\000D\0020\0085\00A0\1680\2000\2001\2002\2003\2004\2005\2006\2007\2008\2009\200A\2028\2029\202F\205F\3000') <> ''
    ),
    CONSTRAINT ck_item_skill_definition_version_description CHECK (
        btrim(description, U&'\0009\000A\000B\000C\000D\0020\0085\00A0\1680\2000\2001\2002\2003\2004\2005\2006\2007\2008\2009\200A\2028\2029\202F\205F\3000') <> ''
    ),
    CONSTRAINT fk_item_skill_definition_version_owner FOREIGN KEY (item_skill_definition_id)
        REFERENCES public.item_skill_definition (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE,
    CONSTRAINT fk_item_skill_definition_version_patch FOREIGN KEY (from_game_patch_id)
        REFERENCES public.game_patch (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE
);

CREATE TABLE public.item_version_skill_link (
    id BIGINT GENERATED ALWAYS AS IDENTITY CONSTRAINT pk_item_version_skill_link PRIMARY KEY,
    item_version_id BIGINT CONSTRAINT nn_item_version_skill_link_item_version NOT NULL,
    item_version_patch_id BIGINT CONSTRAINT nn_item_version_skill_link_patch NOT NULL,
    item_skill_definition_id BIGINT CONSTRAINT nn_item_version_skill_link_definition NOT NULL,
    item_skill_definition_version_id BIGINT CONSTRAINT nn_item_version_skill_link_version NOT NULL,
    description TEXT,
    CONSTRAINT uq_item_version_skill_link_item_definition
        UNIQUE (item_version_id, item_skill_definition_id) NOT DEFERRABLE,
    CONSTRAINT fk_item_version_skill_link_item_patch
        FOREIGN KEY (item_version_id, item_version_patch_id)
        REFERENCES public.item_version (id, from_game_patch_id)
        ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE,
    CONSTRAINT fk_item_version_skill_link_patch FOREIGN KEY (item_version_patch_id)
        REFERENCES public.game_patch (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE,
    CONSTRAINT fk_item_version_skill_link_definition FOREIGN KEY (item_skill_definition_id)
        REFERENCES public.item_skill_definition (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE,
    CONSTRAINT fk_item_version_skill_link_definition_version
        FOREIGN KEY (item_skill_definition_id, item_skill_definition_version_id)
        REFERENCES public.item_skill_definition_version (item_skill_definition_id, id)
        ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE
);

CREATE TRIGGER trg_item_reject_pk_update AFTER UPDATE ON public.item
FOR EACH ROW EXECUTE FUNCTION public.reject_common_pk_update();

CREATE TRIGGER trg_item_version_reject_pk_update AFTER UPDATE ON public.item_version
FOR EACH ROW EXECUTE FUNCTION public.reject_common_pk_update();

CREATE TRIGGER trg_stat_type_reject_pk_update AFTER UPDATE ON public.stat_type
FOR EACH ROW EXECUTE FUNCTION public.reject_common_pk_update();

CREATE TRIGGER trg_item_skill_definition_reject_pk_update AFTER UPDATE ON public.item_skill_definition
FOR EACH ROW EXECUTE FUNCTION public.reject_common_pk_update();

CREATE TRIGGER trg_item_skill_definition_version_reject_pk_update AFTER UPDATE ON public.item_skill_definition_version
FOR EACH ROW EXECUTE FUNCTION public.reject_common_pk_update();

CREATE TRIGGER trg_item_version_skill_link_reject_pk_update AFTER UPDATE ON public.item_version_skill_link
FOR EACH ROW EXECUTE FUNCTION public.reject_common_pk_update();

GRANT SELECT, INSERT, UPDATE ON TABLE
    public.item, public.item_version, public.stat_type, public.item_skill_definition_version
    TO lumia_app;
GRANT SELECT, INSERT ON TABLE public.item_skill_definition TO lumia_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.item_version_skill_link TO lumia_app;
