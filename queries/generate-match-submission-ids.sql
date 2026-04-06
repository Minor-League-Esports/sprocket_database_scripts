UPDATE sprocket.match m
  SET "submissionId" = 'match-' || gen_random_uuid()::text
  WHERE m."matchParentId" IN (
      SELECT mp.id
      FROM sprocket.match_parent mp
      INNER JOIN sprocket.schedule_fixture sf ON sf.id = mp."fixtureId"
      INNER JOIN sprocket.schedule_group sg ON sg.id = sf."scheduleGroupId"
      WHERE sg."parentGroupId" = 340
  )
  AND m."submissionId" IS NULL;
