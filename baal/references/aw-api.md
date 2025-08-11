API Reference (Python)¶
Here’s an API reference for some of the most central components in aw_core, aw_client and aw_server. These are the most important packages in ActivityWatch. A lot of it currently lacks proper docstrings, but it’s a start.

Contents

API Reference (Python)

aw_core

aw_core.models

aw_core.log

aw_core.dirs

aw_client

aw_transform

aw_query

aw_server

aw_server.api

aw_core¶
classaw_core.Event(id: Optional[Union[int, str]] = None, timestamp: Optional[Union[datetime.datetime, str]] = None, duration: Union[datetime.timedelta, int, float] = 0, data: Optional[Dict[str, Any]] = None)[source]¶
Used to represents an event.

propertydata: dict¶
 
propertyduration: datetime.timedelta¶
 
propertyid: Optional[Union[int, str]]¶
 
propertytimestamp: datetime.datetime¶
to_json_dict()→ dict[source]¶
Useful when sending data over the wire. Any mongodb interop should not use do this as it accepts datetimes.

to_json_str()→ str[source]¶
aw_core.models¶
classaw_core.models.Event(id: Optional[Union[int, str]] = None, timestamp: Optional[Union[datetime.datetime, str]] = None, duration: Union[datetime.timedelta, int, float] = 0, data: Optional[Dict[str, Any]] = None)[source]¶
Used to represents an event.

propertydata: dict¶
 
propertyduration: datetime.timedelta¶
 
propertyid: Optional[Union[int, str]]¶
 
propertytimestamp: datetime.datetime¶
to_json_dict()→ dict[source]¶
Useful when sending data over the wire. Any mongodb interop should not use do this as it accepts datetimes.

to_json_str()→ str[source]¶
aw_core.log¶
aw_core.log.get_latest_log_file(name, testing=False)→ Optional[str][source]¶
Returns the filename of the last logfile with name. Useful when you want to read the logfile of another ActivityWatch service.

aw_core.log.get_log_file_path()→ Optional[str][source]¶
DEPRECATED: Use get_latest_log_file instead.

aw_core.log.setup_logging(name: str, testing=False, verbose=False, log_stderr=True, log_file=False)[source]¶
aw_core.dirs¶
aw_core.dirs.ensure_path_exists(path: str)→ None[source]¶
aw_core.dirs.get_cache_dir(module_name: Optional[str] = None)→ str[source]¶
aw_core.dirs.get_config_dir(module_name: Optional[str] = None)→ str[source]¶
aw_core.dirs.get_data_dir(module_name: Optional[str] = None)→ str[source]¶
aw_core.dirs.get_log_dir(module_name: Optional[str] = None)→ str[source]¶
aw_client¶
The aw_client package contains a programmer-friendly wrapper around the servers REST API.

classaw_client.ActivityWatchClient(client_name: str = 'unknown', testing=False, host=None, port=None, protocol='http')[source]¶
connect()[source]¶
create_bucket(bucket_id: str, event_type: str, queued=False)[source]¶
delete_bucket(bucket_id: str, force: bool = False)[source]¶
delete_event(bucket_id: str, event_id: int)→ None[source]¶
disconnect()[source]¶
export_all()→ dict[source]¶
export_bucket(bucket_id)→ dict[source]¶
get_buckets()→ dict[source]¶
get_event(bucket_id: str, event_id: int)→ Optional[aw_core.models.Event][source]¶
get_eventcount(bucket_id: str, limit: int = - 1, start: Optional[datetime.datetime] = None, end: Optional[datetime.datetime] = None)→ int[source]¶
get_events(bucket_id: str, limit: int = - 1, start: Optional[datetime.datetime] = None, end: Optional[datetime.datetime] = None)→ List[aw_core.models.Event][source]¶
get_info()[source]¶
Returns a dict currently containing the keys ‘hostname’ and ‘testing’.

get_setting(key: Optional[str] = None)→ dict[source]¶
heartbeat(bucket_id: str, event: aw_core.models.Event, pulsetime: float, queued: bool = False, commit_interval: Optional[float] = None)→ None[source]¶
Args:
bucket_id: The bucket_id of the bucket to send the heartbeat to event: The actual heartbeat event pulsetime: The maximum amount of time in seconds since the last heartbeat to be merged with the previous heartbeat in aw-server queued: Use the aw-client queue feature to queue events if client loses connection with the server commit_interval: Override default pre-merge commit interval

NOTE: This endpoint can use the failed requests retry queue.
This makes the request itself non-blocking and therefore the function will in that case always returns None.

import_bucket(bucket: dict)→ None[source]¶
insert_event(bucket_id: str, event: aw_core.models.Event)→ None[source]¶
insert_events(bucket_id: str, events: List[aw_core.models.Event])→ None[source]¶
query(query: str, timeperiods: List[Tuple[datetime.datetime, datetime.datetime]], name: Optional[str] = None, cache: bool = False)→ List[Any][source]¶
set_setting(key: str, value: str)→ None[source]¶
setup_bucket(bucket_id: str, event_type: str)[source]¶
wait_for_start(timeout: int = 10)→ None[source]¶
Wait for the server to start by trying to get the server info.

aw_transform¶
The aw_transform package contains transforms used in the query language.

Note

Their function signatures and return types may deviate from how the transforms are actually implemented in the query language. For more details, see aw_query.functions

classaw_transform.Rule(rules: Dict[str, Any])[source]¶
ignore_case: bool¶
match(e: aw_core.models.Event)→ bool[source]¶
regex: Optional[Pattern]¶
select_keys: Optional[List[str]]¶
aw_transform.categorize(events: List[aw_core.models.Event], classes: List[Tuple[List[str], aw_transform.classify.Rule]])→ List[aw_core.models.Event][source]¶
aw_transform.chunk_events_by_key(events: List[aw_core.models.Event], key: str, pulsetime: float = 5.0)→ List[aw_core.models.Event][source]¶
“Chunks” adjacent events together which have the same value for a key, and stores the original events in the subevents key of the new event.

aw_transform.concat(events1, events2)→ List[aw_core.models.Event][source]¶
Concatenates two lists of events

aw_transform.filter_keyvals(events: List[aw_core.models.Event], key: str, vals: List[str], exclude=False)→ List[aw_core.models.Event][source]¶
aw_transform.filter_keyvals_regex(events: List[aw_core.models.Event], key: str, regex: str)→ List[aw_core.models.Event][source]¶
aw_transform.filter_period_intersect(events: List[aw_core.models.Event], filterevents: List[aw_core.models.Event])→ List[aw_core.models.Event][source]¶
Filters away all events or time periods of events in which a filterevent does not have an intersecting time period.

Useful for example when you want to filter away events or part of events during which a user was AFK.

Usage:
windowevents_notafk = filter_period_intersect(windowevents, notafkevents)

Example:
events1   |   =======        ======== |
events2   | ------  ---  ---   ----   |
result    |   ====  =          ====   |
A JavaScript version used to exist in aw-webui but was removed in this PR.

aw_transform.flood(events: List[aw_core.models.Event], pulsetime: float = 5)→ List[aw_core.models.Event][source]¶
Takes a list of events and “floods” any empty space between events by extending one of the surrounding events to cover the empty space.

For more details on flooding, see this issue:
https://github.com/ActivityWatch/activitywatch/issues/124

aw_transform.heartbeat_merge(last_event: aw_core.models.Event, heartbeat: aw_core.models.Event, pulsetime: float)→ Optional[aw_core.models.Event][source]¶
Merges two events if they have identical data and the heartbeat timestamp is within the pulsetime window.

aw_transform.heartbeat_reduce(events: List[aw_core.models.Event], pulsetime: float)→ List[aw_core.models.Event][source]¶
Merges consecutive events together according to the rules of heartbeat_merge.

aw_transform.limit_events(events, count)→ List[aw_core.models.Event][source]¶
Returns the count first events in the list of events

aw_transform.merge_events_by_keys(events, keys)→ List[aw_core.models.Event][source]¶
Sums the duration of all events which share a value for a key and returns a new event for each value.

aw_transform.period_union(events1: List[aw_core.models.Event], events2: List[aw_core.models.Event])→ List[aw_core.models.Event][source]¶
Takes a list of two events and returns a new list of events covering the union of the timeperiods contained in the eventlists with no overlapping events.

Warning

This function strips all data from events as it cannot keep it consistent.

Example:
events1   |   -------       --------- |
events2   | ------  ---  --    ----   |
result    | -----------  -- --------- |
aw_transform.simplify_string(events: List[aw_core.models.Event], key: str = 'title')→ List[aw_core.models.Event][source]¶
aw_transform.sort_by_duration(events)→ List[aw_core.models.Event][source]¶
Sorts a list of events by duration

aw_transform.sort_by_timestamp(events)→ List[aw_core.models.Event][source]¶
Sorts a list of events by timestamp

aw_transform.split_url_events(events: List[aw_core.models.Event])→ List[aw_core.models.Event][source]¶
aw_transform.sum_durations(events)→ datetime.timedelta[source]¶
Sums the durations for the given events

aw_transform.tag(events: List[aw_core.models.Event], classes: List[Tuple[str, aw_transform.classify.Rule]])→ List[aw_core.models.Event][source]¶
aw_transform.union(events1: List[aw_core.models.Event], events2: List[aw_core.models.Event])→ List[aw_core.models.Event][source]¶
Concatenates and sorts union of 2 event lists and removes duplicates.

Example:
Merges events from a backup-bucket with events from a “living” bucket.

events = union(events_backup, events_living)
aw_transform.union_no_overlap(events1: List[aw_core.models.Event], events2: List[aw_core.models.Event])→ List[aw_core.models.Event][source]¶
Merges two eventlists and removes overlap, the first eventlist will have precedence

Example:
events1 | xxx xx xxx | events1 | —- —— – | result | xxx– xx —-xxx – |

aw_query¶
The aw_query package contains the interpreter for the query language and registers the standard functions, usually based on Python implementations of them available in aw_transform.

aw_query.query(name: str, query: str, starttime: datetime.datetime, endtime: datetime.datetime, datastore: aw_datastore.datastore.Datastore)→ Any[source]¶
aw_query.functions.q2_categorize(events: list, classes: list)[source]¶
aw_query.functions.q2_chunk_events_by_key(events: list, key: str)→ List[aw_core.models.Event][source]¶
Note

Documentation automatically copied from underlying function aw_transform.chunk_events_by_key

“Chunks” adjacent events together which have the same value for a key, and stores the original events in the subevents key of the new event.

aw_query.functions.q2_concat(events1: list, events2: list)→ List[aw_core.models.Event][source]¶
Note

Documentation automatically copied from underlying function aw_transform.concat

Concatenates two lists of events

aw_query.functions.q2_exclude_keyvals(events: list, key: str, vals: list)→ List[aw_core.models.Event][source]¶
aw_query.functions.q2_filter_keyvals(events: list, key: str, vals: list)→ List[aw_core.models.Event][source]¶
aw_query.functions.q2_filter_keyvals_regex(events: list, key: str, regex: str)→ List[aw_core.models.Event][source]¶
aw_query.functions.q2_filter_period_intersect(events: list, filterevents: list)→ List[aw_core.models.Event][source]¶
Note

Documentation automatically copied from underlying function aw_transform.filter_period_intersect

Filters away all events or time periods of events in which a filterevent does not have an intersecting time period.

Useful for example when you want to filter away events or part of events during which a user was AFK.

Usage:
windowevents_notafk = filter_period_intersect(windowevents, notafkevents)

Example:
events1   |   =======        ======== |
events2   | ------  ---  ---   ----   |
result    |   ====  =          ====   |
A JavaScript version used to exist in aw-webui but was removed in this PR.

aw_query.functions.q2_find_bucket(datastore: aw_datastore.datastore.Datastore, filter_str: str, hostname: Optional[str] = None)[source]¶
Find bucket by using a filter_str (to avoid hardcoding bucket names)

aw_query.functions.q2_flood(events: list)→ List[aw_core.models.Event][source]¶
Note

Documentation automatically copied from underlying function aw_transform.flood

Takes a list of events and “floods” any empty space between events by extending one of the surrounding events to cover the empty space.

For more details on flooding, see this issue:
https://github.com/ActivityWatch/activitywatch/issues/124

aw_query.functions.q2_limit_events(events: list, count: int)→ List[aw_core.models.Event][source]¶
Note

Documentation automatically copied from underlying function aw_transform.limit_events

Returns the count first events in the list of events

aw_query.functions.q2_merge_events_by_keys(events: list, keys: list)→ List[aw_core.models.Event][source]¶
Note

Documentation automatically copied from underlying function aw_transform.merge_events_by_keys

Sums the duration of all events which share a value for a key and returns a new event for each value.

aw_query.functions.q2_nop()[source]¶
No operation function for unittesting

aw_query.functions.q2_period_union(events1: list, events2: list)→ List[aw_core.models.Event][source]¶
Note

Documentation automatically copied from underlying function aw_transform.period_union

Takes a list of two events and returns a new list of events covering the union of the timeperiods contained in the eventlists with no overlapping events.

Warning

This function strips all data from events as it cannot keep it consistent.

Example:
events1   |   -------       --------- |
events2   | ------  ---  --    ----   |
result    | -----------  -- --------- |
aw_query.functions.q2_query_bucket(datastore: aw_datastore.datastore.Datastore, namespace: Dict[str, Any], bucketname: str)→ List[aw_core.models.Event][source]¶
aw_query.functions.q2_query_bucket_eventcount(datastore: aw_datastore.datastore.Datastore, namespace: Dict[str, Any], bucketname: str)→ int[source]¶
aw_query.functions.q2_simplify_window_titles(events: list, key: str)→ List[aw_core.models.Event][source]¶
aw_query.functions.q2_sort_by_duration(events: list)→ List[aw_core.models.Event][source]¶
Note

Documentation automatically copied from underlying function aw_transform.sort_by_duration

Sorts a list of events by duration

aw_query.functions.q2_sort_by_timestamp(events: list)→ List[aw_core.models.Event][source]¶
Note

Documentation automatically copied from underlying function aw_transform.sort_by_timestamp

Sorts a list of events by timestamp

aw_query.functions.q2_split_url_events(events: list)→ List[aw_core.models.Event][source]¶
aw_query.functions.q2_sum_durations(events: list)→ datetime.timedelta[source]¶
Note

Documentation automatically copied from underlying function aw_transform.sum_durations

Sums the durations for the given events

aw_query.functions.q2_tag(events: list, classes: list)[source]¶
aw_query.functions.q2_union_no_overlap(events1: list, events2: list)→ List[aw_core.models.Event][source]¶
Note

Documentation automatically copied from underlying function aw_transform.union_no_overlap

Merges two eventlists and removes overlap, the first eventlist will have precedence

Example:
events1 | xxx xx xxx | events1 | —- —— – | result | xxx– xx —-xxx – |

aw_server¶
aw_server.main()[source]¶
Called from the executable and __main__.py

aw_server.api¶
The ServerAPI class contains the basic API methods, these methods are primarily called from RPC layers such as the one found in aw_server.rest.

classaw_server.api.ServerAPI(db, testing)[source]¶
create_bucket(bucket_id: str, event_type: str, client: str, hostname: str, created: Optional[datetime.datetime] = None, data: Optional[Dict[str, Any]] = None)→ bool[source]¶
Create a bucket.

If hostname is “!local”, the hostname and device_id will be set from the server info. This is useful for watchers which are known/assumed to run locally but might not know their hostname (like aw-watcher-web).

Returns True if successful, otherwise false if a bucket with the given ID already existed.

create_events(bucket_id: str, events: List[aw_core.models.Event])→ Optional[aw_core.models.Event][source]¶
Create events for a bucket. Can handle both single events and multiple ones.

Returns the inserted event when a single event was inserted, otherwise None.

delete_bucket(bucket_id: str)→ None[source]¶
Delete a bucket

delete_event(bucket_id: str, event_id)→ bool[source]¶
Delete a single event from a bucket

export_all()→ Dict[str, Any][source]¶
Exports all buckets and their events to a format consistent across versions

export_bucket(bucket_id: str)→ Dict[str, Any][source]¶
Export a bucket to a dataformat consistent across versions, including all events in it.

get_bucket_metadata(bucket_id: str)→ Dict[str, Any][source]¶
Get metadata about bucket.

get_buckets()→ Dict[str, Dict][source]¶
Get dict {bucket_name: Bucket} of all buckets

get_event(bucket_id: str, event_id: int)→ Optional[aw_core.models.Event][source]¶
Get a single event from a bucket

get_eventcount(bucket_id: str, start: Optional[datetime.datetime] = None, end: Optional[datetime.datetime] = None)→ int[source]¶
Get eventcount from a bucket

get_events(bucket_id: str, limit: int = - 1, start: Optional[datetime.datetime] = None, end: Optional[datetime.datetime] = None)→ List[aw_core.models.Event][source]¶
Get events from a bucket

get_info()→ Dict[str, Any][source]¶
Get server info

get_log()[source]¶
Get the server log in json format

get_setting(key)[source]¶
Get a setting

heartbeat(bucket_id: str, heartbeat: aw_core.models.Event, pulsetime: float)→ aw_core.models.Event[source]¶
Heartbeats are useful when implementing watchers that simply keep track of a state, how long it’s in that state and when it changes. A single heartbeat always has a duration of zero.

If the heartbeat was identical to the last (apart from timestamp), then the last event has its duration updated. If the heartbeat differed, then a new event is created.

Such as:
Active application and window title - Example: aw-watcher-window

Currently open document/browser tab/playing song - Example: wakatime - Example: aw-watcher-web - Example: aw-watcher-spotify

Is the user active/inactive? Send an event on some interval indicating if the user is active or not. - Example: aw-watcher-afk

Inspired by: https://wakatime.com/developers#heartbeats

import_all(buckets: Dict[str, Any])[source]¶
import_bucket(bucket_data: Any)[source]¶
query2(name, query, timeperiods, cache)[source]¶
set_setting(key, value)[source]¶
Set a setting

update_bucket(bucket_id: str, event_type: Optional[str] = None, client: Optional[str] = None, hostname: Optional[str] = None, data: Optional[Dict[str, Any]] = None)→ None[source]¶