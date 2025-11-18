# Just a Tech Lead doing code review:
This run is a lot better than others as it works, but its still got kinks as mentioned in the review below

`datasets/raw/commercial-backyard-flocks.csv`
Finding Duplicates indicated in report and figuring out why...

```
{
"type": "within-batch",
"external_id": "COMM_3222e86e2831",
"species": "WOAH Non-Poultry",
"date": "2022-05-19 00:00:00",
"county": "Canyon",
"state": "Idaho"
}
```

"Canyon","Idaho","05-19-2022","WOAH Non-Poultry","10"
"Canyon","Idaho","05-19-2022","WOAH Non-Poultry","10"

```
{
"type": "within-batch",
"external_id": "COMM_62decb2e7cc2",
"species": "WOAH Poultry",
"date": "2022-05-17 00:00:00",
"county": "Canyon",
"state": "Idaho"
}
```

`"Canyon","Idaho","05-17-2022","WOAH Poultry","30"`
"Salt Lake","Utah","05-17-2022","WOAH Non-Poultry","30"
`"Canyon","Idaho","05-17-2022","WOAH Non-Poultry","50"`
(removed other detections on this date for brevity)

hmmm this seems more like different detections because of the flock size


```
{
"type": "within-batch",
"external_id": "COMM_4f62a4f92cd8",
"species": "WOAH Non-Poultry",
"date": "2022-05-11 00:00:00",
"county": "Clallam",
"state": "Washington"
}
```

"Cache","Utah","05-11-2022","WOAH Non-Poultry","20"
"Chisago","Minnesota","05-11-2022","WOAH Poultry","160"
`"Clallam","Washington","05-11-2022","WOAH Non-Poultry","10"`
`"Clallam","Washington","05-11-2022","WOAH Non-Poultry","10"`
"Pierce","Washington","05-11-2022","WOAH Non-Poultry","20"
"Ada","Idaho","05-11-2022","WOAH Non-Poultry","4"


```
{
"type": "within-batch",
"external_id": "COMM_5a070c146fc8",
"species": "WOAH Poultry",
"date": "2023-03-14 00:00:00",
"county": "Lancaster",
"state": "Pennsylvania"
}
{
"type": "within-batch",
"external_id": "COMM_80513bbacb4f",
"species": "WOAH Poultry",
"date": "2023-03-14 00:00:00",
"county": "Lancaster",
"state": "Pennsylvania"
}
```
`"Lancaster","Pennsylvania","03-14-2023","WOAH Poultry","3000"`
`"Lancaster","Pennsylvania","03-14-2023","WOAH Poultry","3900"`
`"Lancaster","Pennsylvania","03-14-2023","WOAH Poultry","2400"`
`"Lancaster","Pennsylvania","03-14-2023","WOAH Poultry","2400"`
"Eaton","Michigan","03-14-2023","WOAH Non-Poultry","20"
`"Lancaster","Pennsylvania","03-14-2023","WOAH Poultry","3000"`


```
{
"type": "within-batch",
"external_id": "COMM_d43d41a703cb",
"species": "Commercial Turkey Meat Bird",
"date": "2025-01-15 00:00:00",
"county": "Darke",
"state": "Ohio"
}
```
`"Darke","Ohio","01-15-2025","Commercial Turkey Meat Bird","5300"`
"Owyhee","Idaho","01-15-2025","WOAH Non-Poultry","30"
`"Darke","Ohio","01-15-2025","Commercial Turkey Meat Bird","15800"`
"Mercer","Ohio","01-15-2025","Commercial Turkey Meat Bird","10400"
`"Darke","Ohio","01-15-2025","Commercial Turkey Meat Bird","5300"`
"New London","Connecticut","01-15-2025","WOAH Non-Poultry","20"


```
{
"type": "within-batch",
"external_id": "COMM_40b832942b48",
"species": "WOAH Non-Poultry",
"date": "2025-01-03 00:00:00",
"county": "Canyon",
"state": "Idaho"
},
{
"type": "within-batch",
"external_id": "COMM_40b832942b48",
"species": "WOAH Non-Poultry",
"date": "2025-01-03 00:00:00",
"county": "Canyon",
"state": "Idaho"
}
```

"Pocahontas","West Virginia","01-03-2025","WOAH Poultry","9"
`"Canyon","Idaho","01-03-2025","WOAH Non-Poultry","20"`
"Stanislaus","California","01-03-2025","Commercial Broiler Production","236100"
`"Canyon","Idaho","01-03-2025","WOAH Non-Poultry","20"`
`"Canyon","Idaho","01-03-2025","WOAH Non-Poultry","70"`
"Butte","California","01-03-2025","Commercial Raised for Release Upland Game Bird","38700"
`"Canyon","Idaho","01-03-2025","WOAH Non-Poultry","20"`
"Sharp","Arkansas","01-03-2025","WOAH Non-Poultry","20"

There seems to be a pattern of either the parser or loader getting confused... For the commercial-backyard-flocks datasets, we need to make sure the AI doesn't exlude these record, but instead merges them and adds to that number of detections fields and increases amount affected number.