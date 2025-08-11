-- Postgres function to upsert a plant and replace its care instructions atomically
-- Create this in your Supabase database (SQL editor or migration)
-- Assumes tables: plants(plant_id uuid pk default gen_random_uuid(), plant_name text, zone text, plant_group text, ...)
-- and care_instructions(id uuid pk default gen_random_uuid(), plant_id uuid fk, care_phase text, months text, step_description text, priority text, order_within_season int)

create or replace function public.upsert_plant_and_care(
  plant jsonb,
  care_instructions jsonb,
  lookup jsonb
)
returns jsonb
language plpgsql
security definer
as $$
declare
  v_plant_id uuid;
  v_zone text := nullif(lookup->>'zone', '');
  v_group text := lookup->>'plant_group';
  v_name text := lookup->>'plant_name';
  v_record jsonb;
begin
  if v_group in ('Houseplants', 'Succulents') then
    select plant_id into v_plant_id
    from public.plants
    where plant_name = v_name and plant_group = v_group and zone is null
    limit 1;

    if v_plant_id is null then
      insert into public.plants (
        plant_name, zone, description, type, sun_requirements,
        seed_starting_month, planting_month, seed_starting_instructions,
        planting_instructions, zone_suitability, seasonality, plant_group,
        requirements, seed_starting, planting, care_plan,
        model_used, raw_llm_response
      ) values (
        plant->>'plant_name', null, plant->>'description', plant->>'type', plant->>'sun_requirements',
        plant->>'seed_starting_month', plant->>'planting_month', plant->'seed_starting_instructions',
        plant->'planting_instructions', plant->>'zone_suitability', plant->>'seasonality', plant->>'plant_group',
        plant->'requirements', plant->'seed_starting', plant->'planting', plant->'care_plan',
        plant->>'model_used', plant->'raw_llm_response'
      ) returning plant_id into v_plant_id;
    else
      update public.plants set
        description = plant->>'description',
        type = plant->>'type',
        sun_requirements = plant->>'sun_requirements',
        seed_starting_month = plant->>'seed_starting_month',
        planting_month = plant->>'planting_month',
        seed_starting_instructions = plant->'seed_starting_instructions',
        planting_instructions = plant->'planting_instructions',
        zone_suitability = plant->>'zone_suitability',
        seasonality = plant->>'seasonality',
        plant_group = plant->>'plant_group',
        requirements = plant->'requirements',
        seed_starting = plant->'seed_starting',
        planting = plant->'planting',
        care_plan = plant->'care_plan',
        model_used = plant->>'model_used',
        raw_llm_response = plant->'raw_llm_response'
      where plant_id = v_plant_id;
    end if;
  else
    select plant_id into v_plant_id
    from public.plants
    where plant_name = v_name and zone = v_zone
    limit 1;

    if v_plant_id is null then
      insert into public.plants (
        plant_name, zone, description, type, sun_requirements,
        seed_starting_month, planting_month, seed_starting_instructions,
        planting_instructions, zone_suitability, seasonality, plant_group,
        requirements, seed_starting, planting, care_plan,
        model_used, raw_llm_response
      ) values (
        plant->>'plant_name', v_zone, plant->>'description', plant->>'type', plant->>'sun_requirements',
        plant->>'seed_starting_month', plant->>'planting_month', plant->'seed_starting_instructions',
        plant->'planting_instructions', plant->>'zone_suitability', plant->>'seasonality', plant->>'plant_group',
        plant->'requirements', plant->'seed_starting', plant->'planting', plant->'care_plan',
        plant->>'model_used', plant->'raw_llm_response'
      ) returning plant_id into v_plant_id;
    else
      update public.plants set
        description = plant->>'description',
        type = plant->>'type',
        sun_requirements = plant->>'sun_requirements',
        seed_starting_month = plant->>'seed_starting_month',
        planting_month = plant->>'planting_month',
        seed_starting_instructions = plant->'seed_starting_instructions',
        planting_instructions = plant->'planting_instructions',
        zone_suitability = plant->>'zone_suitability',
        seasonality = plant->>'seasonality',
        plant_group = plant->>'plant_group',
        requirements = plant->'requirements',
        seed_starting = plant->'seed_starting',
        planting = plant->'planting',
        care_plan = plant->'care_plan',
        model_used = plant->>'model_used',
        raw_llm_response = plant->'raw_llm_response'
      where plant_id = v_plant_id;
    end if;
  end if;

  -- Replace care instructions
  delete from public.care_instructions where plant_id = v_plant_id;

  if care_instructions is not null then
    insert into public.care_instructions (
      plant_id, care_phase, months, step_description, priority, order_within_season
    )
    select v_plant_id,
           (ci->>'care_phase')::text,
           nullif(ci->>'months',''),
           (ci->>'step_description')::text,
           nullif(ci->>'priority',''),
           coalesce((ci->>'order_within_season')::int, 1)
    from jsonb_array_elements(coalesce(care_instructions, '[]'::jsonb)) as ci;
  end if;

  v_record := jsonb_build_object('plant_id', v_plant_id);
  return v_record;
end;
$$;

-- Optional: grant execute to anon/service roles
-- grant execute on function public.upsert_plant_and_care(jsonb, jsonb, jsonb) to anon, service_role;


