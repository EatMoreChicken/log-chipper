# Log Chipper
Log Chipper is an application designed as a proof-of-concept to utilize LLMs (Language Model Models) for generating test logs based on a small set of provided sample logs.

**YouTube Intro**
[![Youtube Intro](https://img.youtube.com/vi/ygBcdcMeJPo/0.jpg)](https://www.youtube.com/watch?v=ygBcdcMeJPo)

The app currently leverages GPT3.5, but there are plans to incorporate additional compatibility in the future.

## How it Works
### Old Method
The old method utilizes LLMs to analyze the sample log set and generate test logs through the following process:

1. Gather log samples from a data source.
2. Provide the log samples to the LLM.
3. Prompt the LLM to generate test logs.

**Pros**
- Easy to use.
- Fast for small batches.

**Cons**
- Slow for large batches.
- Uses a large number of tokens.
- Log formatting and timestamping tend to be inconsistent.

### New Method
The new method improves upon the old approach by leveraging LLMs to analyze the sample log set and generate a programmatic template. The updated process is as follows:

1. Gather log samples from a data source.
2. Provide the log samples to the LLM.
3. Prompt the LLM to generate a log format template and allowed values based on the provided samples.
4. Utilize a script to generate consistent test logs using the template.

**Pros**
- Relatively easy to use and update formatting.
- More consistent speed compared to the old method.
- Uses fewer tokens overall.
- Log and timestamp formatting is consistent.

**Cons**
- Requires a bit more upfront work to set up.

## How to Use
### Setup
1. Install the required dependencies by running `pip install -r requirements.txt`.
2. Generate an OpenAI API token and populate the `openai.api_key` variable in `app.py` with your API key.
3. Run the application using `python3 app.py`.
4. Access the Web GUI at `http://127.0.0.1:5000`.

### Generating Log Templates
To generate log templates, follow these steps:

1. Gather sample logs to use when generating a template.
   - Use logs with a similar format: The same data source could generate various log formats, and each template should correspond to a specific format. For example, firewall logs could have multiple templates for different log formats it generates.
   - Have some variety: Choose sample logs with some variety, as the allowed values are selected from these samples you provide. You can always add your own values, but it's easier if the template can generate them in the first place.

2. Paste the sample logs into the `Sample Logs` text box and click **Generate Config**. The process may take a few seconds to generate the config.

3. The generated config will be displayed in the **Log Template Config** text box. Complete the following steps:
   - [ ] Ensure that the section header (e.g., `[example_header]`) is a unique name. If the section header already exists in the `data/local/templates.ini` file, this new config will overwrite it.
   - [ ] Ensure that the `{date}` variable appears in the `format_string`. The `{date}` variable should include the date and time without being broken up. For example, a format like `{month} {date} {time}` will not work. If necessary, click **Generate Config** until it generates the correct date format or manually create the `{date}` variable in the `format_string` and adjust the `start_date` and `allowed_values_date` parameters accordingly.
   - [ ] Ensure that the following required fields are present and valid: `format_string`, `start_date`, `min_interval_seconds`, `max_interval_seconds`, `allowed_values_date`.
   - [ ] Update `min_interval_seconds` and `max_interval_seconds` as needed. The script will randomly choose an integer between these values to determine the time elapsed between events.
   - [ ] Ensure all fields in the `format_string` have corresponding `allowed_values_<field-name>` entries.

4. Click **Save** and **Generate Logs**. You can check the `generate_logs.log` file for script logs and errors. Additionally, you can manually update the config within the `data/local/templates.ini` file. Currently, the GUI cannot automatically pull the updated config from the `ini` file, so you must copy it to the **Log Template Config** text box before generating logs using a new template.

## Example Templates
Here is an example of a log template configuration in the `ini` format:

```ini
[log_template_1]
format_string = {date} {hostname} {ipv4} {event} for "{user}"
start_date = January 02 2022 00:08:12
min_interval_seconds = 2
max_interval_seconds = 5
allowed_values_date = %%B %%d %%Y %%H:%%M:%%S
allowed_values_hostname = hostname1, hostname2, hostname3
allowed_values_ipv4 = 1.0.0.1, 192.168.1.1, 10.0.0.1
allowed_values_event = Login Successful, Login Failure
allowed_values_user = user1, user2, user3
```

## Other Notes
- You can change the *System Prompt* by updating the `system_prompt` variable in `app.py`.
- Currently, the application only utilizes GPT3.5.
- All templates are saved in `data/local/templates.ini` currently.

## To-Do
- [ ] Implement a `format_string` to ensure all expected variables and values are present in the config.
- [ ] Update the script to pull expected variables from the `format_string` instead of having the LLM generate it.
- [ ] Implement logic to split `data/local/templates.ini` into 
- [ ] Add visual cues in the Web GUI to indicate when logs are being generated.
- [ ] Create a better method for handling API Keys (e.g., utilizing another INI file or environmental variable).
- [ ] Implement a method to retrieve templates from disk to the web GUI.
- [ ] Explore Langchain for potential integration.
- [ ] Create an API endpoint to generate logs based on the section name.
- [ ] Implement GUI configuration similar to Node-RED for creating a "story" with the order of events and specific timings.
- [ ] Set up "Destinations" to forward logs using TCP/UDP.
- [ ] Display errors in the GUI for easier troubleshooting.