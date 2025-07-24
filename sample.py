# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import google.cloud.storage_control_v2
from google.api_core.exceptions import GoogleAPIError


def get_project_intelligence_config_sample(project_id: str):
    """Gets the project-scoped intelligence configuration.

    Args:
        project_id: The ID of the Google Cloud project.
    """
    # Create a client
    client = google.cloud.storage_control_v2.StorageControlClient()

    # The name of the IntelligenceConfig resource associated with your project.
    # Format: projects/{project_id}/locations/global/intelligenceConfig
    name = f"projects/{project_id}/locations/global/intelligenceConfig"

    # [START storage_v2_storagecontrol_projectintelligenceconfig_get]
    try:
        request = \
            google.cloud.storage_control_v2.GetProjectIntelligenceConfigRequest(
                name=name,
            )

        response = client.get_project_intelligence_config(request=request)

        print(f"Retrieved Project Intelligence Config: {response.name}")
        print(f"Edition Config: {response.edition_config}")
        print(f"Update Time: {response.update_time}")
    except GoogleAPIError as e:
        print(f"Error getting project intelligence config: {e}")
    # [END storage_v2_storagecontrol_projectintelligenceconfig_get]