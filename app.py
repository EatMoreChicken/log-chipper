from flask import Flask, render_template, request, send_from_directory, jsonify
import openai
import os
import configparser
import logging
from datetime import datetime, timedelta
import random

# Configure logging
logging.basicConfig(filename='generate_logs.log', level=logging.ERROR)

# Create Flask app
app = Flask(__name__)

# Set OpenAI API key
openai.api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# Alternatively, you can use an environment variable for the API key
# openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the system prompt for log generation
system_prompt = "I am going to give you a sample log and want you to replace values in the sample log using {} with the type of data it is inside the brackets. Here is an example:\\nJanuary 02 2022 00:07:41 hostname3 10.0.0.1 Login Failure for \"user1\"\\nJanuary 02 2022 00:07:42 hostname2 192.168.1.1 Login Successful for \"user2\"\\nYou should generate the following INI for the example above:\\n[login_event_template]\\nformat_string = {date} {hostname} {ipv4} {eventtype} for \"{user}\"\\nstart_date = January 02 2022 00:08:12\\nmin_interval_seconds = 2\\nmax_interval_seconds = 5\\nallowed_values_date = %%B %%d %%Y %%H:%%M:%%S\\nallowed_values_hostname = hostname1, hostname2, hostname3\\nallowed_values_ipv4 = 1.0.0.1, 192.168.1.1, 10.0.0.1\\nallowed_values_eventtype = Login Successful, Login Failure\\nallowed_values_user = user1, user2, user3\\nAug 12 11:52:52 mail vpopmail[4162]: vchkpw-pop3: vpopmail user not found support@:69.3.64.3\\nAug 12 11:52:51 mail vpopmail[4162]: test-pop3: username1 user not found support@:12.3.41.3\\nYou should generate the following INI for the example above:\\n[login_event_template]\\nformat_string = {date} {hostname} {service}[{pid}]: {eventtype} user not found {user}@{ipv4}\\nstart_date = Aug 12 11:54:02\\nmin_interval_seconds = 1\\nmax_interval_seconds = 10\\nallowed_values_date = %%b %%d %%H:%%M:%%S\\nallowed_values_hostname = mail\\nallowed_values_service = vpopmail\\nallowed_values_pid = 4162\\nallowed_values_eventtype = vchkpw-pop3:\\nallowed_values_user = support\\nallowed_values_ipv4 = 69.3.64.3\\nAdditional Requirements:\\n- The following fields are required for every template: format_string, start_date, min_interval_seconds, max_interval_seconds, allowed_values_date\\n- Only give me the INI file in a code block. Nothing else.\\n- The \"date\" should be kept as one value, do now split up into sub sections.\\n- Make sure all fields in the format string have allowed values in the INI.\\\n- Make sure to adhere to the example format I provided.\\n- Make sure all variables for formating are in the \"format_string\". The \"allowed_values_\" parameters should only have values."

def generate_log_message(template_name):
    try:
        # Define the file path for the templates
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/local/templates.ini")

        # Read the template configurations from the file
        config = configparser.ConfigParser()
        config.read(file_path)

        # Retrieve the specified template
        template = config[template_name]
        format_string = template["format_string"]
        start_date_str = template.get("start_date", config.get(template_name, "start_date"))

        # Parse the start date and interval values
        start_date = datetime.strptime(start_date_str, template.get("allowed_values_date", config.get(template_name, "allowed_values_date")))
        min_interval = int(template.get("min_interval_seconds", config.get(template_name, "min_interval_seconds")))
        max_interval = int(template.get("max_interval_seconds", config.get(template_name, "max_interval_seconds")))

        kwargs = {}

        # Iterate over the template keys
        for key in template:
            # Extract the allowed values for each key
            if key.startswith("allowed_values_"):
                allowed_values = template[key].split(", ")
                kwargs[key[len("allowed_values_"):]] = random.choice(allowed_values)

        # Format the log message using the template and provided values
        current_date_str = start_date.strftime(template.get("allowed_values_date", config.get(template_name, "allowed_values_date")))
        kwargs["date"] = datetime.strptime(current_date_str, template.get("allowed_values_date", config.get(template_name, "allowed_values_date"))).strftime(template.get("allowed_values_date", config.get(template_name, "allowed_values_date")))
        log_message = format_string.format(**kwargs)

        # Update the start date for the template
        start_date = start_date + timedelta(seconds=random.randint(min_interval, max_interval))
        template["start_date"] = start_date.strftime(template.get("allowed_values_date", config.get(template_name, "allowed_values_date")))
        config.set(template_name, "start_date", start_date.strftime(template.get("allowed_values_date", config.get(template_name, "allowed_values_date"))))

        # Write the updated template configurations back to the file
        with open(file_path, "w") as f:
            config.write(f)

        # Return the generated log message
        return log_message
    except Exception as e:
        # Log any errors that occur during log message generation
        logging.exception("An error occurred while generating a log message: {}".format(e), exc_info=False)
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Retrieve the sample logs from the form
        sample_logs = request.form['sample_logs']

        # Define the messages for the conversation with OpenAI Chat API
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": sample_logs}
        ]

        # Generate a response from the Chat API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or whichever engine you're using
            messages=messages,
            max_tokens=2048  # set appropriate max tokens as per your needs
        )

        # Extract the generated log format from the response
        config = response['choices'][0]['message']['content'].strip()

        # Render the index.html template with the generated log format and sample logs
        return render_template('index.html', config=config, sample_logs=sample_logs)

    # Render the index.html template with an empty config (initial page load)
    return render_template('index.html', config='')


@app.route('/generate-config', methods=['POST'])
def generate_config():
    # Retrieve the sample logs from the form
    sample_logs = request.form['sample_logs']

    # Define the messages for the conversation with OpenAI Chat API
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": sample_logs}
    ]

    # Generate a response from the Chat API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or whichever engine you're using
        messages=messages,
        max_tokens=2048  # set appropriate max tokens as per your needs
    )

    # Extract the generated log format from the response
    config = response['choices'][0]['message']['content'].strip()

    # Return the generated log format as JSON
    return jsonify({'config': config})

@app.route('/favicon.ico')
def favicon():
    # Serve the favicon.ico file
    return send_from_directory(os.path.join(app.root_path, 'static'), 'static/images/favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/generate_logs', methods=['POST'])
def generate_logs():
    # Retrieve the config string from the form
    config_string = request.form.get('config')

    # Parse the config string using configparser
    config_parser = configparser.RawConfigParser()
    config_parser.read_string(config_string)

    # Retrieve the template name from the config
    sections = config_parser.sections()
    template_name = sections[0]

    # Generate 10 log messages using the template
    log_messages = ""
    for i in range(10):
        log_message = generate_log_message(template_name)
        if log_message is not None:
            log_messages += log_message + "\n"

    # Return the generated log messages as JSON
    return jsonify({'generated_logs': log_messages})

@app.route('/save-config', methods=['POST'])
def save_config():
    # Retrieve the config text from the form
    config_text = request.form.get('config')

    try:
        # Validate that the input string is in INI format
        new_config = configparser.ConfigParser()
        new_config.read_string(config_text)

        # Determine the absolute file path
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/local/templates.ini")

        # Check if the stanza name already exists in the INI file
        existing_config = configparser.ConfigParser()
        existing_config.read(file_path)

        # Remove existing stanza if it exists
        for section in new_config.sections():
            if section in existing_config.sections():
                existing_config.remove_section(section)

        # Combine existing and new config
        existing_config.read_string(config_text)

        # Write the updated config to the file
        with open(file_path, "w") as f:
            existing_config.write(f)

        print("INI data updated.")

        return jsonify({'result': 'success'})

    except configparser.Error as e:
        print("Invalid INI format.")
        return jsonify({'error': 'Invalid INI format: ' + str(e)})

    except ValueError as e:
        print("Error saving config:", e)
        return jsonify({'error': 'Error saving config: ' + str(e)})

    except Exception as e:
        print("Error saving config:", e)
        return jsonify({'error': 'Error saving config: ' + str(e)})


if __name__ == '__main__':
    # Run the Flask app in debug mode
    app.run(debug=True)
