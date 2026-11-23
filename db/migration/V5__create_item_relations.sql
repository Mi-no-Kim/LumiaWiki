ALTER TABLE public.item_version
    ADD COLUMN material_a_item_id BIGINT,
    ADD COLUMN material_a_version_id BIGINT,
    ADD COLUMN material_b_item_id BIGINT,
    ADD COLUMN material_b_version_id BIGINT,
    ADD COLUMN craft_output_count INTEGER,
    ADD COLUMN delivery_acquire_count INTEGER,
    ADD COLUMN deliverable BOOLEAN,
    ADD COLUMN delivery_price INTEGER,
    ADD CONSTRAINT ck_item_version_recipe_complete CHECK (
        num_nonnulls(material_a_item_id, material_a_version_id, material_b_item_id,
                     material_b_version_id, craft_output_count) IN (0, 5)
    ),
    ADD CONSTRAINT ck_item_version_recipe_materials CHECK (material_a_item_id <> material_b_item_id),
    ADD CONSTRAINT ck_item_version_delivery_price CHECK (delivery_price IS NULL OR deliverable IS TRUE),
    ADD CONSTRAINT fk_item_version_material_a FOREIGN KEY (material_a_item_id, material_a_version_id)
        REFERENCES public.item_version (item_id, id)
        ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE,
    ADD CONSTRAINT fk_item_version_material_b FOREIGN KEY (material_b_item_id, material_b_version_id)
        REFERENCES public.item_version (item_id, id)
        ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE;

CREATE INDEX ix_item_version_material_a ON public.item_version (material_a_item_id);
CREATE INDEX ix_item_version_material_b ON public.item_version (material_b_item_id);

CREATE TYPE public.acquisition_method AS ENUM ('GATHERING', 'CHEST', 'HUNTING');
CREATE TYPE public.acquisition_method_range AS RANGE (SUBTYPE = public.acquisition_method);

CREATE TABLE public.item_acquisition (
    id BIGINT GENERATED ALWAYS AS IDENTITY CONSTRAINT pk_item_acquisition PRIMARY KEY,
    item_id BIGINT NOT NULL,
    item_version_id BIGINT NOT NULL,
    game_patch_id BIGINT NOT NULL,
    method public.acquisition_method NOT NULL,
    region_id BIGINT,
    spawn_count INTEGER,
    CONSTRAINT ck_item_acquisition_method_details CHECK (
        (method = 'CHEST' AND region_id IS NOT NULL)
        OR (method IN ('GATHERING', 'HUNTING') AND spawn_count IS NULL)
    ),
    CONSTRAINT fk_item_acquisition_item FOREIGN KEY (item_id) REFERENCES public.item (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE,
    CONSTRAINT fk_item_acquisition_version_owner FOREIGN KEY (item_id, item_version_id)
        REFERENCES public.item_version (item_id, id)
        ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE,
    CONSTRAINT fk_item_acquisition_version_patch FOREIGN KEY (item_version_id, game_patch_id)
        REFERENCES public.item_version (id, from_game_patch_id)
        ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE,
    CONSTRAINT fk_item_acquisition_patch FOREIGN KEY (game_patch_id) REFERENCES public.game_patch (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE,
    CONSTRAINT fk_item_acquisition_region FOREIGN KEY (region_id) REFERENCES public.region (id)
        ON DELETE RESTRICT ON UPDATE NO ACTION NOT DEFERRABLE,
    CONSTRAINT ex_item_acquisition_region EXCLUDE USING gist (
        (numrange(item_version_id::numeric, item_version_id::numeric, '[]')) WITH =,
        (public.acquisition_method_range(method, method, '[]')) WITH =,
        (numrange(region_id::numeric, region_id::numeric, '[]')) WITH &&
    )
);

CREATE INDEX ix_item_acquisition_version ON public.item_acquisition (item_version_id);

CREATE TRIGGER trg_item_acquisition_reject_pk_update AFTER UPDATE ON public.item_acquisition
FOR EACH ROW EXECUTE FUNCTION public.reject_common_pk_update();

REVOKE USAGE ON TYPE public.acquisition_method, public.acquisition_method_range FROM PUBLIC;
GRANT USAGE ON TYPE public.acquisition_method TO lumia_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.item_acquisition TO lumia_app;
