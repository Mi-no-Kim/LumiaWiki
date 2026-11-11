CREATE TABLE `region` (
	`region_id`	BIGINT	NOT NULL,
	`name`	VARCHAR(100)	NOT NULL,
	`polygon_coordinates`	JSON	NULL,
	`hyperloop_exists`	BOOLEAN	NOT NULL,
	`kiosk_exists`	BOOLEAN	NOT NULL
);

CREATE TABLE `character_stat` (
	`id`	BIGINT	NOT NULL,
	`character_id`	BIGINT	NOT NULL,
	`stat_type_id`	BIGINT	NOT NULL,
	`level1_value`	DECIMAL(10,2)	NULL,
	`growth_value`	DECIMAL(10,2)	NULL
);

CREATE TABLE `season` (
	`season_id`	BIGINT	NOT NULL,
	`season_name`	VARCHAR(100)	NULL,
	`created_at`	DATETIME	NULL,
	`sort_order`	BIGINT	NULL
);

CREATE TABLE `region_name_version` (
	`id`	BIGINT	NOT NULL,
	`region_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`name`	VARCHAR(100)	NOT NULL
);

CREATE TABLE `character_skill_content_version` (
	`id`	BIGINT	NOT NULL,
	`skill_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`description`	VARCHAR(500)	NOT NULL,
	`formula`	VARCHAR(500)	NULL,
	`variable`	JSON	NULL
);

CREATE TABLE `item_region_spawn` (
	`id`	BIGINT	NOT NULL,
	`item_id`	BIGINT	NOT NULL,
	`region_id`	BIGINT	NOT NULL,
	`count`	INT	NOT NULL
);

CREATE TABLE `item_rank` (
	`id`	BIGINT	NOT NULL,
	`name`	VARCHAR(100)	NOT NULL,
	`sort_order`	BIGINT	NOT NULL
);

CREATE TABLE `region_connection` (
	`id`	BIGINT	NOT NULL,
	`region_from_id`	BIGINT	NOT NULL,
	`region_to_id`	BIGINT	NOT NULL,
	`connection_type`	VARCHAR(100)	NOT NULL
);

CREATE TABLE `trait_content_version` (
	`id`	BIGINT	NOT NULL,
	`trait_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`description`	VARCHAR(500)	NOT NULL,
	`formula`	VARCHAR(500)	NULL
);

CREATE TABLE `trait_name_version` (
	`id`	BIGINT	NOT NULL,
	`trait_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`name`	VARCHAR(100)	NOT NULL
);

CREATE TABLE `character_skill` (
	`skill_id`	BIGINT	NOT NULL,
	`character_id`	BIGINT	NOT NULL,
	`skill_name`	VARCHAR(100)	NOT NULL,
	`skill_type`	VARCHAR(20)	NOT NULL	COMMENT '스킬 구분값, 정확한 체계 미정',
	`description`	VARCHAR(500)	NOT NULL,
	`image_url`	VARCHAR(500)	NOT NULL,
	`formula`	VARCHAR(500)	NULL,
	`variable`	JSON	NULL
);

CREATE TABLE `item_type` (
	`id`	BIGINT	NOT NULL,
	`parent_id`	BIGINT	NULL	COMMENT '상위 종류 (self-reference, nullable = 최상위)',
	`name`	VARCHAR(100)	NOT NULL,
	`sort_order`	BIGINT	NOT NULL,
	`visible`	BOOLEAN	NOT NULL
);

CREATE TABLE `item_extra_version` (
	`id`	BIGINT	NOT NULL,
	`item_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`item_type_id`	BIGINT	NOT NULL,
	`item_rank_id`	BIGINT	NOT NULL,
	`inventory_limit`	INT	NULL,
	`create_count`	INT	NULL,
	`delivery_acquire_count`	INT	NULL,
	`deliverable`	BOOLEAN	NULL,
	`delivery_price`	INT	NULL
);

CREATE TABLE `character_name_version` (
	`id`	BIGINT	NOT NULL,
	`character_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`name`	VARCHAR(100)	NOT NULL
);

CREATE TABLE `item_leaf_materials` (
	`id`	BIGINT	NOT NULL,
	`item_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`leaf_item_id`	BIGINT	NOT NULL,
	`quantity`	INT	NOT NULL	COMMENT '동일 재료 중복 사용 시 합산된 수량'
);

CREATE TABLE `item_stat` (
	`id`	BIGINT	NOT NULL,
	`item_id`	BIGINT	NOT NULL,
	`stat_type_id`	BIGINT	NOT NULL,
	`value`	DECIMAL(10,2)	NOT NULL
);

CREATE TABLE `special_stat_content_version` (
	`id`	BIGINT	NOT NULL,
	`special_stat_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`description`	VARCHAR(500)	NOT NULL,
	`formula`	VARCHAR(500)	NULL
);

CREATE TABLE `character_skill_image_version` (
	`id`	BIGINT	NOT NULL,
	`skill_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`image_url`	VARCHAR(500)	NOT NULL
);

CREATE TABLE `item_image_version` (
	`id`	BIGINT	NOT NULL,
	`item_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`image_url`	VARCHAR(500)	NOT NULL
);

CREATE TABLE `item_recipe_version` (
	`id`	BIGINT	NOT NULL,
	`item_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`material_left_id`	BIGINT	NULL,
	`material_right_id`	BIGINT	NULL
);

CREATE TABLE `region_content_version` (
	`id`	BIGINT	NOT NULL,
	`region_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`polygon_coordinates`	JSON	NULL	COMMENT '경계 좌표, 형식 미정',
	`hyperloop_exists`	BOOLEAN	NOT NULL,
	`kiosk_exists`	BOOLEAN	NOT NULL
);

CREATE TABLE `trait` (
	`trait_id`	BIGINT	NOT NULL,
	`trait_path_id`	BIGINT	NOT NULL,
	`name`	VARCHAR(100)	NOT NULL,
	`image_url`	VARCHAR(500)	NOT NULL,
	`trait_type`	VARCHAR(20)	NOT NULL	COMMENT 'main/sub',
	`description`	VARCHAR(500)	NOT NULL,
	`formula`	VARCHAR(500)	NULL
);

CREATE TABLE `item_special_stat` (
	`id`	BIGINT	NOT NULL,
	`item_id`	BIGINT	NOT NULL,
	`special_stat_id`	BIGINT	NOT NULL,
	`variable`	JSON	NOT NULL
);

CREATE TABLE `item_stat_version` (
	`id`	BIGINT	NOT NULL,
	`item_id`	BIGINT	NOT NULL,
	`stat_type_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`value`	DECIMAL(10,2)	NOT NULL
);

CREATE TABLE `character` (
	`character_id`	BIGINT	NOT NULL,
	`created_version_id`	BIGINT	NOT NULL,
	`name`	VARCHAR(100)	NOT NULL
);

CREATE TABLE `character_stat_version` (
	`id`	BIGINT	NOT NULL,
	`character_id`	BIGINT	NOT NULL,
	`stat_type_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`level1_value`	DECIMAL(10,2)	NULL,
	`growth_value`	DECIMAL(10,2)	NULL
);

CREATE TABLE `trait_path` (
	`trait_path_id`	BIGINT	NOT NULL,
	`name`	VARCHAR(100)	NOT NULL,
	`color`	VARCHAR(20)	NULL,
	`image_url`	VARCHAR(500)	NULL
);

CREATE TABLE `region_connection_version` (
	`id`	BIGINT	NOT NULL,
	`region_from_id`	BIGINT	NOT NULL,
	`region_to_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`connection_type`	VARCHAR(100)	NOT NULL
);

CREATE TABLE `stat_type` (
	`id`	BIGINT	NOT NULL,
	`name`	VARCHAR(100)	NOT NULL,
	`sort_order`	INT	NOT NULL
);

CREATE TABLE `special_stat` (
	`id`	BIGINT	NOT NULL,
	`name`	VARCHAR(100)	NOT NULL,
	`description`	VARCHAR(500)	NOT NULL,
	`formula`	VARCHAR(500)	NULL
);

CREATE TABLE `item` (
	`id`	BIGINT	NOT NULL,
	`item_type_id`	BIGINT	NOT NULL,
	`item_rank_id`	BIGINT	NOT NULL,
	`name`	VARCHAR(200)	NOT NULL,
	`image_url`	VARCHAR(500)	NOT NULL,
	`stat_json`	JSON	NOT NULL,
	`description`	VARCHAR(500)	NULL,
	`inventory_limit`	INT	NULL,
	`create_count`	INT	NULL,
	`delivery_acquire_count`	INT	NULL,
	`deliverable`	BOOLEAN	NULL,
	`delivery_price`	INT	NULL,
	`searchable`	BOOLEAN	NOT NULL,
	`is_deleted`	BOOLEAN	NOT NULL,
	`material_left_id`	BIGINT	NULL,
	`material_right_id`	BIGINT	NULL
);

CREATE TABLE `trait_image_version` (
	`id`	BIGINT	NOT NULL,
	`trait_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`image_url`	VARCHAR(500)	NOT NULL
);

CREATE TABLE `weapon_type` (
	`id`	BIGINT	NOT NULL,
	`name`	VARCHAR(100)	NOT NULL,
	`sort_order`	BIGINT	NOT NULL,
	`item_type_id`	BIGINT	NOT NULL
);

CREATE TABLE `special_stat_name_version` (
	`id`	BIGINT	NOT NULL,
	`special_stat_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`name`	VARCHAR(100)	NOT NULL
);

CREATE TABLE `patch_note` (
	`patch_note_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`raw_text`	TEXT	NOT NULL
);

CREATE TABLE `item_region_spawn_version` (
	`id`	BIGINT	NOT NULL,
	`item_id`	BIGINT	NOT NULL,
	`region_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`count`	INT	NOT NULL
);

CREATE TABLE `weapon_skill` (
	`id`	BIGINT	NOT NULL,
	`weapon_type_id`	BIGINT	NOT NULL,
	`name`	VARCHAR(100)	NOT NULL,
	`description`	VARCHAR(500)	NOT NULL,
	`image_url`	VARCHAR(500)	NOT NULL,
	`formula`	VARCHAR(500)	NULL,
	`variable`	JSON	NULL
);

CREATE TABLE `weapon_skill_image_version` (
	`id`	BIGINT	NOT NULL,
	`weapon_skill_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`image_url`	VARCHAR(500)	NOT NULL
);

CREATE TABLE `system_formula` (
	`formula_id`	BIGINT	NOT NULL,
	`name`	VARCHAR(200)	NOT NULL,
	`formula_value`	TEXT	NOT NULL	COMMENT '현재값만 저장, 이력 없음. IndexedDB로 사용자 로컬 수정 가능'
);

CREATE TABLE `item_name_version` (
	`id`	BIGINT	NOT NULL,
	`item_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`name`	VARCHAR(200)	NOT NULL
);

CREATE TABLE `weapon_skill_content_version` (
	`id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`weapon_skill_id`	BIGINT	NOT NULL,
	`description`	VARCHAR(500)	NOT NULL,
	`formula`	VARCHAR(500)	NULL,
	`variable`	JSON	NULL
);

CREATE TABLE `weapon_skill_name_version` (
	`id`	BIGINT	NOT NULL,
	`weapon_skill_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`name`	VARCHAR(100)	NOT NULL
);

CREATE TABLE `change_log` (
	`id`	BIGINT	NOT NULL,
	`parent_id`	BIGINT	NULL	COMMENT '상위-하위 계층 (self-reference, nullable)',
	`entity_type`	VARCHAR(50)	NOT NULL	COMMENT '실험체/스킬/아이템/특성 등 (polymorphic)',
	`entity_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`change_type`	VARCHAR(20)	NOT NULL	COMMENT '버프/너프/조정/변경/추가/삭제 (6종)',
	`description`	TEXT	NULL,
	`source`	VARCHAR(20)	NULL	COMMENT '수동/반자동/자동'
);

CREATE TABLE `character_weapon_type_version` (
	`id`	BIGINT	NOT NULL,
	`character_id`	BIGINT	NOT NULL,
	`weapon_type_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL
);

CREATE TABLE `item_special_stat_version` (
	`id`	BIGINT	NOT NULL,
	`item_id`	BIGINT	NOT NULL,
	`special_stat_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`variable`	JSON	NOT NULL
);

CREATE TABLE `character_skill_name_version` (
	`id`	BIGINT	NOT NULL,
	`skill_id`	BIGINT	NOT NULL,
	`version_id`	BIGINT	NOT NULL,
	`name`	VARCHAR(100)	NOT NULL
);

CREATE TABLE `character_weapon_type` (
	`id`	BIGINT	NOT NULL,
	`weapon_type_id`	BIGINT	NOT NULL,
	`character_id`	BIGINT	NOT NULL
);

CREATE TABLE `version` (
	`version_id`	BIGINT	NOT NULL,
	`season_id`	BIGINT	NOT NULL,
	`version_name`	VARCHAR(100)	NOT NULL,
	`created_at`	DATETIME	NOT NULL	COMMENT '패치 반영 시간. 서버 시간과 비교해 현재/예정 판정, status enum 없음',
	`sort_order`	BIGINT	NULL
);

CREATE TABLE `patch_note_fragment` (
	`fragment_id`	BIGINT	NOT NULL,
	`patch_note_id`	BIGINT	NOT NULL,
	`entity_type`	VARCHAR(50)	NULL	COMMENT '실험체/아이템/지역 등',
	`entity_id`	BIGINT	NULL,
	`content`	TEXT	NULL
);

ALTER TABLE `region` ADD CONSTRAINT `PK_REGION` PRIMARY KEY (
	`region_id`
);

ALTER TABLE `character_stat` ADD CONSTRAINT `PK_CHARACTER_STAT` PRIMARY KEY (
	`id`
);

ALTER TABLE `season` ADD CONSTRAINT `PK_SEASON` PRIMARY KEY (
	`season_id`
);

ALTER TABLE `region_name_version` ADD CONSTRAINT `PK_REGION_NAME_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `character_skill_content_version` ADD CONSTRAINT `PK_CHARACTER_SKILL_CONTENT_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `item_region_spawn` ADD CONSTRAINT `PK_ITEM_REGION_SPAWN` PRIMARY KEY (
	`id`
);

ALTER TABLE `item_rank` ADD CONSTRAINT `PK_ITEM_RANK` PRIMARY KEY (
	`id`
);

ALTER TABLE `region_connection` ADD CONSTRAINT `PK_REGION_CONNECTION` PRIMARY KEY (
	`id`
);

ALTER TABLE `trait_content_version` ADD CONSTRAINT `PK_TRAIT_CONTENT_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `trait_name_version` ADD CONSTRAINT `PK_TRAIT_NAME_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `character_skill` ADD CONSTRAINT `PK_CHARACTER_SKILL` PRIMARY KEY (
	`skill_id`
);

ALTER TABLE `item_type` ADD CONSTRAINT `PK_ITEM_TYPE` PRIMARY KEY (
	`id`
);

ALTER TABLE `item_extra_version` ADD CONSTRAINT `PK_ITEM_EXTRA_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `character_name_version` ADD CONSTRAINT `PK_CHARACTER_NAME_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `item_leaf_materials` ADD CONSTRAINT `PK_ITEM_LEAF_MATERIALS` PRIMARY KEY (
	`id`
);

ALTER TABLE `item_stat` ADD CONSTRAINT `PK_ITEM_STAT` PRIMARY KEY (
	`id`
);

ALTER TABLE `special_stat_content_version` ADD CONSTRAINT `PK_SPECIAL_STAT_CONTENT_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `character_skill_image_version` ADD CONSTRAINT `PK_CHARACTER_SKILL_IMAGE_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `item_image_version` ADD CONSTRAINT `PK_ITEM_IMAGE_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `item_recipe_version` ADD CONSTRAINT `PK_ITEM_RECIPE_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `region_content_version` ADD CONSTRAINT `PK_REGION_CONTENT_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `trait` ADD CONSTRAINT `PK_TRAIT` PRIMARY KEY (
	`trait_id`
);

ALTER TABLE `item_special_stat` ADD CONSTRAINT `PK_ITEM_SPECIAL_STAT` PRIMARY KEY (
	`id`
);

ALTER TABLE `item_stat_version` ADD CONSTRAINT `PK_ITEM_STAT_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `character` ADD CONSTRAINT `PK_CHARACTER` PRIMARY KEY (
	`character_id`
);

ALTER TABLE `character_stat_version` ADD CONSTRAINT `PK_CHARACTER_STAT_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `trait_path` ADD CONSTRAINT `PK_TRAIT_PATH` PRIMARY KEY (
	`trait_path_id`
);

ALTER TABLE `region_connection_version` ADD CONSTRAINT `PK_REGION_CONNECTION_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `stat_type` ADD CONSTRAINT `PK_STAT_TYPE` PRIMARY KEY (
	`id`
);

ALTER TABLE `special_stat` ADD CONSTRAINT `PK_SPECIAL_STAT` PRIMARY KEY (
	`id`
);

ALTER TABLE `item` ADD CONSTRAINT `PK_ITEM` PRIMARY KEY (
	`id`
);

ALTER TABLE `trait_image_version` ADD CONSTRAINT `PK_TRAIT_IMAGE_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `weapon_type` ADD CONSTRAINT `PK_WEAPON_TYPE` PRIMARY KEY (
	`id`
);

ALTER TABLE `special_stat_name_version` ADD CONSTRAINT `PK_SPECIAL_STAT_NAME_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `patch_note` ADD CONSTRAINT `PK_PATCH_NOTE` PRIMARY KEY (
	`patch_note_id`
);

ALTER TABLE `item_region_spawn_version` ADD CONSTRAINT `PK_ITEM_REGION_SPAWN_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `weapon_skill` ADD CONSTRAINT `PK_WEAPON_SKILL` PRIMARY KEY (
	`id`
);

ALTER TABLE `weapon_skill_image_version` ADD CONSTRAINT `PK_WEAPON_SKILL_IMAGE_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `system_formula` ADD CONSTRAINT `PK_SYSTEM_FORMULA` PRIMARY KEY (
	`formula_id`
);

ALTER TABLE `item_name_version` ADD CONSTRAINT `PK_ITEM_NAME_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `weapon_skill_content_version` ADD CONSTRAINT `PK_WEAPON_SKILL_CONTENT_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `weapon_skill_name_version` ADD CONSTRAINT `PK_WEAPON_SKILL_NAME_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `change_log` ADD CONSTRAINT `PK_CHANGE_LOG` PRIMARY KEY (
	`id`
);

ALTER TABLE `character_weapon_type_version` ADD CONSTRAINT `PK_CHARACTER_WEAPON_TYPE_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `item_special_stat_version` ADD CONSTRAINT `PK_ITEM_SPECIAL_STAT_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `character_skill_name_version` ADD CONSTRAINT `PK_CHARACTER_SKILL_NAME_VERSION` PRIMARY KEY (
	`id`
);

ALTER TABLE `character_weapon_type` ADD CONSTRAINT `PK_CHARACTER_WEAPON_TYPE` PRIMARY KEY (
	`id`
);

ALTER TABLE `version` ADD CONSTRAINT `PK_VERSION` PRIMARY KEY (
	`version_id`
);

ALTER TABLE `patch_note_fragment` ADD CONSTRAINT `PK_PATCH_NOTE_FRAGMENT` PRIMARY KEY (
	`fragment_id`
);

ALTER TABLE `character_stat` ADD CONSTRAINT `FK_character_TO_character_stat_1` FOREIGN KEY (
	`character_id`
)
REFERENCES `character` (
	`character_id`
);

ALTER TABLE `character_stat` ADD CONSTRAINT `FK_stat_type_TO_character_stat_1` FOREIGN KEY (
	`stat_type_id`
)
REFERENCES `stat_type` (
	`id`
);

ALTER TABLE `region_name_version` ADD CONSTRAINT `FK_region_TO_region_name_version_1` FOREIGN KEY (
	`region_id`
)
REFERENCES `region` (
	`region_id`
);

ALTER TABLE `region_name_version` ADD CONSTRAINT `FK_version_TO_region_name_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `character_skill_content_version` ADD CONSTRAINT `FK_character_skill_TO_character_skill_content_version_1` FOREIGN KEY (
	`skill_id`
)
REFERENCES `character_skill` (
	`skill_id`
);

ALTER TABLE `character_skill_content_version` ADD CONSTRAINT `FK_version_TO_character_skill_content_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `item_region_spawn` ADD CONSTRAINT `FK_item_TO_item_region_spawn_1` FOREIGN KEY (
	`item_id`
)
REFERENCES `item` (
	`id`
);

ALTER TABLE `item_region_spawn` ADD CONSTRAINT `FK_region_TO_item_region_spawn_1` FOREIGN KEY (
	`region_id`
)
REFERENCES `region` (
	`region_id`
);

ALTER TABLE `region_connection` ADD CONSTRAINT `FK_region_TO_region_connection_1` FOREIGN KEY (
	`region_from_id`
)
REFERENCES `region` (
	`region_id`
);

ALTER TABLE `region_connection` ADD CONSTRAINT `FK_region_TO_region_connection_2` FOREIGN KEY (
	`region_to_id`
)
REFERENCES `region` (
	`region_id`
);

ALTER TABLE `trait_content_version` ADD CONSTRAINT `FK_trait_TO_trait_content_version_1` FOREIGN KEY (
	`trait_id`
)
REFERENCES `trait` (
	`trait_id`
);

ALTER TABLE `trait_content_version` ADD CONSTRAINT `FK_version_TO_trait_content_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `trait_name_version` ADD CONSTRAINT `FK_trait_TO_trait_name_version_1` FOREIGN KEY (
	`trait_id`
)
REFERENCES `trait` (
	`trait_id`
);

ALTER TABLE `trait_name_version` ADD CONSTRAINT `FK_version_TO_trait_name_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `character_skill` ADD CONSTRAINT `FK_character_TO_character_skill_1` FOREIGN KEY (
	`character_id`
)
REFERENCES `character` (
	`character_id`
);

ALTER TABLE `item_type` ADD CONSTRAINT `FK_item_type_TO_item_type_1` FOREIGN KEY (
	`parent_id`
)
REFERENCES `item_type` (
	`id`
);

ALTER TABLE `item_extra_version` ADD CONSTRAINT `FK_item_TO_item_extra_version_1` FOREIGN KEY (
	`item_id`
)
REFERENCES `item` (
	`id`
);

ALTER TABLE `item_extra_version` ADD CONSTRAINT `FK_version_TO_item_extra_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `item_extra_version` ADD CONSTRAINT `FK_item_type_TO_item_extra_version_1` FOREIGN KEY (
	`item_type_id`
)
REFERENCES `item_type` (
	`id`
);

ALTER TABLE `item_extra_version` ADD CONSTRAINT `FK_item_rank_TO_item_extra_version_1` FOREIGN KEY (
	`item_rank_id`
)
REFERENCES `item_rank` (
	`id`
);

ALTER TABLE `character_name_version` ADD CONSTRAINT `FK_character_TO_character_name_version_1` FOREIGN KEY (
	`character_id`
)
REFERENCES `character` (
	`character_id`
);

ALTER TABLE `character_name_version` ADD CONSTRAINT `FK_version_TO_character_name_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `item_leaf_materials` ADD CONSTRAINT `FK_item_TO_item_leaf_materials_1` FOREIGN KEY (
	`item_id`
)
REFERENCES `item` (
	`id`
);

ALTER TABLE `item_leaf_materials` ADD CONSTRAINT `FK_item_TO_item_leaf_materials_2` FOREIGN KEY (
	`leaf_item_id`
)
REFERENCES `item` (
	`id`
);

ALTER TABLE `item_leaf_materials` ADD CONSTRAINT `FK_version_TO_item_leaf_materials_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `item_stat` ADD CONSTRAINT `FK_item_TO_item_stat_1` FOREIGN KEY (
	`item_id`
)
REFERENCES `item` (
	`id`
);

ALTER TABLE `item_stat` ADD CONSTRAINT `FK_stat_type_TO_item_stat_1` FOREIGN KEY (
	`stat_type_id`
)
REFERENCES `stat_type` (
	`id`
);

ALTER TABLE `special_stat_content_version` ADD CONSTRAINT `FK_special_stat_TO_special_stat_content_version_1` FOREIGN KEY (
	`special_stat_id`
)
REFERENCES `special_stat` (
	`id`
);

ALTER TABLE `special_stat_content_version` ADD CONSTRAINT `FK_version_TO_special_stat_content_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `character_skill_image_version` ADD CONSTRAINT `FK_character_skill_TO_character_skill_image_version_1` FOREIGN KEY (
	`skill_id`
)
REFERENCES `character_skill` (
	`skill_id`
);

ALTER TABLE `character_skill_image_version` ADD CONSTRAINT `FK_version_TO_character_skill_image_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `item_image_version` ADD CONSTRAINT `FK_item_TO_item_image_version_1` FOREIGN KEY (
	`item_id`
)
REFERENCES `item` (
	`id`
);

ALTER TABLE `item_image_version` ADD CONSTRAINT `FK_version_TO_item_image_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `item_recipe_version` ADD CONSTRAINT `FK_item_TO_item_recipe_version_1` FOREIGN KEY (
	`item_id`
)
REFERENCES `item` (
	`id`
);

ALTER TABLE `item_recipe_version` ADD CONSTRAINT `FK_item_TO_item_recipe_version_2` FOREIGN KEY (
	`material_left_id`
)
REFERENCES `item` (
	`id`
);

ALTER TABLE `item_recipe_version` ADD CONSTRAINT `FK_item_TO_item_recipe_version_3` FOREIGN KEY (
	`material_right_id`
)
REFERENCES `item` (
	`id`
);

ALTER TABLE `item_recipe_version` ADD CONSTRAINT `FK_version_TO_item_recipe_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `region_content_version` ADD CONSTRAINT `FK_region_TO_region_content_version_1` FOREIGN KEY (
	`region_id`
)
REFERENCES `region` (
	`region_id`
);

ALTER TABLE `region_content_version` ADD CONSTRAINT `FK_version_TO_region_content_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `trait` ADD CONSTRAINT `FK_trait_path_TO_trait_1` FOREIGN KEY (
	`trait_path_id`
)
REFERENCES `trait_path` (
	`trait_path_id`
);

ALTER TABLE `item_special_stat` ADD CONSTRAINT `FK_item_TO_item_special_stat_1` FOREIGN KEY (
	`item_id`
)
REFERENCES `item` (
	`id`
);

ALTER TABLE `item_special_stat` ADD CONSTRAINT `FK_special_stat_TO_item_special_stat_1` FOREIGN KEY (
	`special_stat_id`
)
REFERENCES `special_stat` (
	`id`
);

ALTER TABLE `item_stat_version` ADD CONSTRAINT `FK_item_TO_item_stat_version_1` FOREIGN KEY (
	`item_id`
)
REFERENCES `item` (
	`id`
);

ALTER TABLE `item_stat_version` ADD CONSTRAINT `FK_stat_type_TO_item_stat_version_1` FOREIGN KEY (
	`stat_type_id`
)
REFERENCES `stat_type` (
	`id`
);

ALTER TABLE `item_stat_version` ADD CONSTRAINT `FK_version_TO_item_stat_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `character` ADD CONSTRAINT `FK_version_TO_character_1` FOREIGN KEY (
	`created_version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `character_stat_version` ADD CONSTRAINT `FK_character_TO_character_stat_version_1` FOREIGN KEY (
	`character_id`
)
REFERENCES `character` (
	`character_id`
);

ALTER TABLE `character_stat_version` ADD CONSTRAINT `FK_stat_type_TO_character_stat_version_1` FOREIGN KEY (
	`stat_type_id`
)
REFERENCES `stat_type` (
	`id`
);

ALTER TABLE `character_stat_version` ADD CONSTRAINT `FK_version_TO_character_stat_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `region_connection_version` ADD CONSTRAINT `FK_region_TO_region_connection_version_1` FOREIGN KEY (
	`region_from_id`
)
REFERENCES `region` (
	`region_id`
);

ALTER TABLE `region_connection_version` ADD CONSTRAINT `FK_region_TO_region_connection_version_2` FOREIGN KEY (
	`region_to_id`
)
REFERENCES `region` (
	`region_id`
);

ALTER TABLE `region_connection_version` ADD CONSTRAINT `FK_version_TO_region_connection_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `item` ADD CONSTRAINT `FK_item_type_TO_item_1` FOREIGN KEY (
	`item_type_id`
)
REFERENCES `item_type` (
	`id`
);

ALTER TABLE `item` ADD CONSTRAINT `FK_item_rank_TO_item_1` FOREIGN KEY (
	`item_rank_id`
)
REFERENCES `item_rank` (
	`id`
);

ALTER TABLE `item` ADD CONSTRAINT `FK_item_TO_item_1` FOREIGN KEY (
	`material_left_id`
)
REFERENCES `item` (
	`id`
);

ALTER TABLE `item` ADD CONSTRAINT `FK_item_TO_item_2` FOREIGN KEY (
	`material_right_id`
)
REFERENCES `item` (
	`id`
);

ALTER TABLE `trait_image_version` ADD CONSTRAINT `FK_trait_TO_trait_image_version_1` FOREIGN KEY (
	`trait_id`
)
REFERENCES `trait` (
	`trait_id`
);

ALTER TABLE `trait_image_version` ADD CONSTRAINT `FK_version_TO_trait_image_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `weapon_type` ADD CONSTRAINT `FK_item_type_TO_weapon_type_1` FOREIGN KEY (
	`item_type_id`
)
REFERENCES `item_type` (
	`id`
);

ALTER TABLE `special_stat_name_version` ADD CONSTRAINT `FK_special_stat_TO_special_stat_name_version_1` FOREIGN KEY (
	`special_stat_id`
)
REFERENCES `special_stat` (
	`id`
);

ALTER TABLE `special_stat_name_version` ADD CONSTRAINT `FK_version_TO_special_stat_name_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `patch_note` ADD CONSTRAINT `FK_version_TO_patch_note_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `item_region_spawn_version` ADD CONSTRAINT `FK_item_TO_item_region_spawn_version_1` FOREIGN KEY (
	`item_id`
)
REFERENCES `item` (
	`id`
);

ALTER TABLE `item_region_spawn_version` ADD CONSTRAINT `FK_region_TO_item_region_spawn_version_1` FOREIGN KEY (
	`region_id`
)
REFERENCES `region` (
	`region_id`
);

ALTER TABLE `item_region_spawn_version` ADD CONSTRAINT `FK_version_TO_item_region_spawn_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `weapon_skill` ADD CONSTRAINT `FK_weapon_type_TO_weapon_skill_1` FOREIGN KEY (
	`weapon_type_id`
)
REFERENCES `weapon_type` (
	`id`
);

ALTER TABLE `weapon_skill_image_version` ADD CONSTRAINT `FK_weapon_skill_TO_weapon_skill_image_version_1` FOREIGN KEY (
	`weapon_skill_id`
)
REFERENCES `weapon_skill` (
	`id`
);

ALTER TABLE `weapon_skill_image_version` ADD CONSTRAINT `FK_version_TO_weapon_skill_image_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `item_name_version` ADD CONSTRAINT `FK_item_TO_item_name_version_1` FOREIGN KEY (
	`item_id`
)
REFERENCES `item` (
	`id`
);

ALTER TABLE `item_name_version` ADD CONSTRAINT `FK_version_TO_item_name_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `weapon_skill_content_version` ADD CONSTRAINT `FK_version_TO_weapon_skill_content_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `weapon_skill_content_version` ADD CONSTRAINT `FK_weapon_skill_TO_weapon_skill_content_version_1` FOREIGN KEY (
	`weapon_skill_id`
)
REFERENCES `weapon_skill` (
	`id`
);

ALTER TABLE `weapon_skill_name_version` ADD CONSTRAINT `FK_weapon_skill_TO_weapon_skill_name_version_1` FOREIGN KEY (
	`weapon_skill_id`
)
REFERENCES `weapon_skill` (
	`id`
);

ALTER TABLE `weapon_skill_name_version` ADD CONSTRAINT `FK_version_TO_weapon_skill_name_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `change_log` ADD CONSTRAINT `FK_change_log_TO_change_log_1` FOREIGN KEY (
	`parent_id`
)
REFERENCES `change_log` (
	`id`
);

ALTER TABLE `change_log` ADD CONSTRAINT `FK_version_TO_change_log_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `character_weapon_type_version` ADD CONSTRAINT `FK_character_TO_character_weapon_type_version_1` FOREIGN KEY (
	`character_id`
)
REFERENCES `character` (
	`character_id`
);

ALTER TABLE `character_weapon_type_version` ADD CONSTRAINT `FK_weapon_type_TO_character_weapon_type_version_1` FOREIGN KEY (
	`weapon_type_id`
)
REFERENCES `weapon_type` (
	`id`
);

ALTER TABLE `character_weapon_type_version` ADD CONSTRAINT `FK_version_TO_character_weapon_type_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `item_special_stat_version` ADD CONSTRAINT `FK_item_TO_item_special_stat_version_1` FOREIGN KEY (
	`item_id`
)
REFERENCES `item` (
	`id`
);

ALTER TABLE `item_special_stat_version` ADD CONSTRAINT `FK_special_stat_TO_item_special_stat_version_1` FOREIGN KEY (
	`special_stat_id`
)
REFERENCES `special_stat` (
	`id`
);

ALTER TABLE `item_special_stat_version` ADD CONSTRAINT `FK_version_TO_item_special_stat_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `character_skill_name_version` ADD CONSTRAINT `FK_character_skill_TO_character_skill_name_version_1` FOREIGN KEY (
	`skill_id`
)
REFERENCES `character_skill` (
	`skill_id`
);

ALTER TABLE `character_skill_name_version` ADD CONSTRAINT `FK_version_TO_character_skill_name_version_1` FOREIGN KEY (
	`version_id`
)
REFERENCES `version` (
	`version_id`
);

ALTER TABLE `character_weapon_type` ADD CONSTRAINT `FK_weapon_type_TO_character_weapon_type_1` FOREIGN KEY (
	`weapon_type_id`
)
REFERENCES `weapon_type` (
	`id`
);

ALTER TABLE `character_weapon_type` ADD CONSTRAINT `FK_character_TO_character_weapon_type_1` FOREIGN KEY (
	`character_id`
)
REFERENCES `character` (
	`character_id`
);

ALTER TABLE `version` ADD CONSTRAINT `FK_season_TO_version_1` FOREIGN KEY (
	`season_id`
)
REFERENCES `season` (
	`season_id`
);

ALTER TABLE `patch_note_fragment` ADD CONSTRAINT `FK_patch_note_TO_patch_note_fragment_1` FOREIGN KEY (
	`patch_note_id`
)
REFERENCES `patch_note` (
	`patch_note_id`
);

