-- Store the role on the category so renaming its display name does not change item slots.
ALTER TABLE public.item_category
    ADD COLUMN equipment_role TEXT,
    ADD CONSTRAINT ck_item_category_equipment_role
        CHECK (equipment_role IN ('ROOT', 'WEAPON', 'CHEST', 'HEAD', 'ACCESSORY', 'LEG'));

UPDATE public.item_category SET equipment_role = 'ROOT' WHERE name = '장비';

UPDATE public.item_category AS branch
SET equipment_role = CASE branch.name
    WHEN '무기' THEN 'WEAPON'
    WHEN '옷' THEN 'CHEST'
    WHEN '머리' THEN 'HEAD'
    WHEN '장식' THEN 'ACCESSORY'
    WHEN '팔' THEN 'ACCESSORY'
    WHEN '다리' THEN 'LEG'
END
FROM public.item_category AS root
WHERE root.id = branch.parent_id AND root.equipment_role = 'ROOT'
    AND branch.name IN ('무기', '옷', '머리', '장식', '팔', '다리');

ALTER TABLE public.item_version DROP COLUMN equipment_slot;
