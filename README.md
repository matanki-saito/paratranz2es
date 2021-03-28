# Trasnlation data importer

Import paratranz translation data to elasticsearch single cluster.

See [discordbot](https://github.com/matanki-saito/discordbot) for details.

## Schedule

The task is performed by github-actions every 3 hours.

## Sources

|  Index  | Project Code and link  | Project Credit | Search Prefix | owner |
| - | - | - | - | - |
| 1 | [76](https://paratranz.cn/projects/76) | EU4_JPM_PROJECT | eu4 | gnagaoka |
| 2 | [91](https://paratranz.cn/projects/91) | CK2_JPM_PROJECT | ck2 | gnagaoka |
| 3 | [335](https://paratranz.cn/projects/335) | Imperator: Rome 日本語化Mod製作プロジェクト | ir | clamm |
| 4 | [350](https://paratranz.cn/projects/350) | Imperator: Rome 日本語化Mod製作プロジェクト | ir | clamm |
| 5 | [2063](https://paratranz.cn/projects/2063) | [Hearts of Iron IV Japanese Language mod](https://docs.google.com/spreadsheets/d/1JW4rjNH4SVspSxvh2wobucvzdVY74o0eJQoI2QGf4n8/edit#gid=476393799) | hoi4 | Inarizushi |
| 6 | [500](https://paratranz.cn/projects/500) | +JP: Kaiserreich | kr | Inarizushi |
| 7 | [1518](https://paratranz.cn/projects/1518) | CK3_JPM_PROJECT | ck3 | gnagaoka |

## Environments

This script receives the secret in the environment variable.The port number (9200) and user name (elastic) cannot be changed.

| Enviroinment Name | description | example |
| - | - | - |
| PARATRANZ_SECRET | paratranz API key | 6966dfca20cb0fb18a255ad45a125bb9 |
| ELASTICSEARCH_HOST | elasticsearch cluster host | localhost |
| ELASTICSEARCH_PASSWORD | elasticsearch cluster password | hogehoge |
