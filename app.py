import streamlit as st
import pandas as pd
from functionforDownloadButtons import download_button
import requests
import re


def _max_width_():
    max_width_str = f"max-width: 1800px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )


def process_bio(text):
	url = "https://text-analysis12.p.rapidapi.com/ner/api/v1.1"

	payload = {
		"language": "english",
		"text": text
	}
	headers = {
		"content-type": "application/json",
		"X-RapidAPI-Key": st.secrets.api_key,
		"X-RapidAPI-Host": "text-analysis12.p.rapidapi.com"
	}

	response = requests.request("POST", url, json=payload, headers=headers)

	df_temp = pd.DataFrame(response.json()['ner'])
	df_temp['ent_length'] = df_temp.end_idx - df_temp.start_idx

	if "PERSON" in df_temp.label.values:
		name = df_temp.loc[df_temp[df_temp.label.eq("PERSON")]["ent_length"].idxmax()].entity
	else:
		name = ""

	if "ORG" in df_temp.label.values:
		org = df_temp.loc[df_temp[df_temp.label.eq("ORG")]["ent_length"].idxmin()].entity
	else:
		org = ""

	if "GPE" in df_temp.label.values:
		location = df_temp.loc[df_temp[df_temp.label.eq("GPE")]["ent_length"].idxmax()].entity
	else:
		location = ""

	rgx = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')
	match = re.search(rgx, text)

	if match is not None:
		email = match.group(0)
	else:
		email = ""
	

	return name, org, location, email

# ------------ Begin app ---------------

st.set_page_config(page_icon="https://i0.wp.com/data-for-humans.com/wp-content/uploads/2022/01/cropped-open_hand_icon_sq.png?ssl=1&resize=438%2C438", page_title="CSV Wrangler")

st.markdown('''
    <a href="https://www.data-for-humans.com">
        <img src="https://i0.wp.com/data-for-humans.com/wp-content/uploads/2022/01/open_hand_logo_titled_xsm-2.png?fit=300%2C37&ssl=1" />
    </a>''',
    unsafe_allow_html=True
)

st.title("Automating Repetitive Data Tasks")

st.markdown("In this example app, we take a .csv file containing professional biographies of individuals and automatically extract relevant data such as name, email, and the organization they work for.")

c29, c30, c31 = st.columns([1, 6, 1])

with c30:

    uploaded_file = st.file_uploader(
        "",
        key="1",
        help="To activate 'wide mode', go to the hamburger menu > Settings > turn on 'wide mode'",
    )

    if uploaded_file is not None:
        file_container = st.expander("Check your uploaded .csv")
        shows = pd.read_csv(uploaded_file)
        uploaded_file.seek(0)
        file_container.write(shows)
        st.dataframe(shows)

    else:
        st.info(
            f"""
                👆 Upload a .csv file first. The .csv should contain a single column of professional bios.  Sample to try: [bios.csv](https://data-for-humans.com/wp-content/uploads/2023/03/bios.csv)
                """
        )

        st.stop()

st.subheader("Working... Extracted data will appear below 👇 ")

df = shows.copy()

df['name'] = ""
df['org'] = ""
df['location'] = ""
df['email'] = ""

for i in range(len(df)):
    name, org, location, email = process_bio(df.iloc[i, 0])
    df.loc[i, 'name'] = name
    df.loc[i, 'org'] = org
    df.loc[i, 'location'] = location
    df.loc[i, 'email'] = email

df = df[['name', 'org', 'location', 'email', 'bio']]

st.text("")

st.dataframe(df)

st.text("")

c29, c30, c31 = st.columns([1, 1, 2])

with c29:

    CSVButton = download_button(
        df,
        "extracted_bios.csv",
        "Download to CSV",
    )

with c30:
    CSVButton = download_button(
        df,
        "extracted_bios.txt",
        "Download to TXT",
    )

with c31:
	st.markdown('''
        <a href="https://www.data-for-humans.com">
            <img src="https://i0.wp.com/data-for-humans.com/wp-content/uploads/2022/01/open_hand_logo_titled_xsm-2.png?fit=300%2C37&ssl=1" />
        </a>''',
        unsafe_allow_html=True
    )

st.markdown("Is your organization faced with a lot of repetitive data tasks?  [Reach out](https://www.data-for-humans.com/contact/) to see how we can help!")