# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import webapp2
from google.cloud import bigquery

class MainPage(webapp2.RequestHandler):
    client = bigquery.Client()
    dataset_id = 'heart_rate'
    table_id = 'heart_rate_bpm'
    table_ref = client.dataset(dataset_id).table(table_id)
    table = client.get_table(table_ref)

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('test!')

    def post(self):
        user_id = self.request.get("user_id")
        bpm = self.request.get("bpm")
        email = self.request.get("email")
        user_event_timestamp = self.request.get("timestamp")
        aggregated_for = self.request.get("aggregated_for")

        row_to_insert = [
            (user_id, email, bpm, user_event_timestamp, aggregated_for)
        ]

        errors = client.insert_rows(table, row_to_insert)

        self.response.headers['Content-Type'] = 'Application/json'

        self.response.write({'result': "ok", 'errors': errors})


app = webapp2.WSGIApplication([
    ('/bpm', MainPage),
], debug=True)
