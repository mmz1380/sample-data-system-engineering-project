#!/bin/bash
clickhouse-client --query="
CREATE TABLE IF NOT EXISTS default.houses (
    id Int32,
    area Int32,
    number_of_bedroom Float32,
    number_of_bathroom Float32,
    year String,
    plot_size Int32,
    floor Int32,
    is_plot_owned Boolean,
    parking_lot_owned Int32,
    is_single_unit Boolean,
    person_id Int32,
    time_stamp DateTime
) ENGINE = MergeTree()
ORDER BY id;
"
