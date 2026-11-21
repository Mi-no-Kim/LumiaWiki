-- Product migration for version attributes and exact item stats.
-- Apply only after the complete structure and the execution target have been confirmed.
-- No existing data is filled in by this migration.

ALTER TABLE public.item_version
    ADD COLUMN grade_id BIGINT,
    ADD COLUMN equipment_slot TEXT,
    ADD COLUMN max_stack_size INTEGER,
    ADD CONSTRAINT fk_item_version_grade FOREIGN KEY (grade_id)
        REFERENCES public.item_grade (id) ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE,
    ADD CONSTRAINT ck_item_version_equipment_slot
        CHECK (equipment_slot IN ('WEAPON', 'CHEST', 'HEAD', 'ACCESSORY', 'LEG')),
    ADD CONSTRAINT ck_item_version_max_stack_size CHECK (max_stack_size > 0);

CREATE TABLE public.item_stat (
    id BIGINT GENERATED ALWAYS AS IDENTITY CONSTRAINT pk_item_stat PRIMARY KEY,
    item_version_id BIGINT CONSTRAINT nn_item_stat_version NOT NULL,
    stat_type_id BIGINT CONSTRAINT nn_item_stat_type NOT NULL,
    value NUMERIC CONSTRAINT nn_item_stat_value NOT NULL,
    CONSTRAINT uq_item_stat_version_type UNIQUE (item_version_id, stat_type_id) NOT DEFERRABLE,
    CONSTRAINT ck_item_stat_finite CHECK (value NOT IN ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric)),
    CONSTRAINT fk_item_stat_version FOREIGN KEY (item_version_id)
        REFERENCES public.item_version (id) ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE,
    CONSTRAINT fk_item_stat_type FOREIGN KEY (stat_type_id)
        REFERENCES public.stat_type (id) ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE
);

CREATE INDEX ix_item_stat_type_version ON public.item_stat (stat_type_id, item_version_id);

CREATE TRIGGER trg_item_stat_reject_pk_update AFTER UPDATE ON public.item_stat
FOR EACH ROW EXECUTE FUNCTION public.reject_common_pk_update();

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.item_stat TO lumia_app;
