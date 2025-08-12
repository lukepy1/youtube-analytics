resource "aws_cloudwatch_event_rule" "youtube_ingest_schedule" {
  name                = "youtube-ingest-schedule"
  description         = "Trigger YouTube ingest Lambda every 30 minutes from 8am to 4pm EST"
  schedule_expression = "cron(0,30 12-20 ? * * *)"
}

resource "aws_cloudwatch_event_target" "youtube_ingest_target" {
  rule      = aws_cloudwatch_event_rule.youtube_ingest_schedule.name
  target_id = "youtube-ingest-lambda"
  arn       = aws_lambda_function.ingest_youtube_data.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingest_youtube_data.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.youtube_ingest_schedule.arn
}
