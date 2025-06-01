import csv
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

# --- Configuration ---
USER_NAMES = [fake.unique.first_name() + "_" + fake.unique.last_name()[:1] for _ in range(20)]
TEAM_NAMES = ["Team Phoenix", "Team Griffin", "Team Hydra", "Marketing", "Cross-functional", "Operations"]
JIRA_TYPES = ["Story", "Task", "Bug", "Feature", "Epic", "Project", "Business Outcome"]
JIRA_PRIORITIES = ["Minor", "Major", "Critical", "Low", "Medium", "High"]
JIRA_STATUSES = ["Pending", "Development", "Review", "Release", "Closed", "Blocked", "Open", "In Progress"]
CR_STATES = ["New", "Assess", "Authorise", "Scheduled", "Implement", "Closed"]
CR_TYPES = ["Standard", "Emergency", "Normal"]
CR_CATEGORIES = ["Enhancement", "BugFix", "Security", "Infrastructure", "Deployment", "Audit", "Maintenance", "New Feature", "Communication"]
CR_RISKS = ["Low", "Medium", "High"]
JIRA_LINK_TYPES = ["blocks", "relates to", "duplicates", "sub-task of", "cloned by"]
CONFLUENCE_SPACES = ["Project Nova", "Team Phoenix KB", "Team Griffin Design", "Team Hydra Compliance", "General Fintech Policies"]

# --- Helper Functions ---
def generate_random_date(start_date=datetime(2023, 1, 1), end_date=datetime(2024, 6, 30)):
    return fake.date_between_dates(date_start=start_date, date_end=end_date)

def generate_semicolon_delimited_list(source_list, max_items=3):
    if not source_list:
        return ""
    num_items = random.randint(0, min(max_items, len(source_list)))
    return ";".join(random.sample(source_list, num_items)) if num_items > 0 else ""

# --- Data Storage for Linking ---
generated_cr_ids = []
generated_jira_ids_unique = [] # Stores unique JIRA IDs before duplication for links/watchers
generated_confluence_ids = []

# --- CSV Generation Functions ---

def generate_cr_main_csv(filename="CR_Main.csv", num_unique_crs=22):
    global generated_cr_ids
    header = [
        'CR_ID', 'CR_Title', 'Linked_Jira_ID', 'Linked_Confluence_ID', 'CR_State',
        'CR_Requested_By', 'CR_Team_Assignment_Group', 'CR_Assigned_To_User',
        'CR_Impacted_Environment', 'CR_Impacted_Departments', 'CR_Type', 'CR_Category',
        'CR_Risk', 'CR_Risk_Percentage', 'CR_Lead_Time_Days', 'CR_Conflict_Status',
        'CR_Description', 'CR_Start_Date', 'CR_End_Date',
        'CR_Implementation_Plan_Summary', 'CR_Backout_Plan_Summary',
        'CR_Updated_By_User_From_CSV_Example', 'CR_Created_At_From_CSV_Example'
    ]
    rows = []
    cr_id_counter = 1

    team_cr_counts = {team: 0 for team in ["Team Phoenix", "Team Griffin", "Team Hydra"]}
    target_team_crs = 7 # Target CRs per main team

    for i in range(num_unique_crs):
        cr_id_base = f"CR-FS-{cr_id_counter:03d}"
        generated_cr_ids.append(cr_id_base)
        cr_id_counter += 1

        title = fake.sentence(nb_words=5, variable_nb_words=True)[:-1]
        # Assign to a main team first until targets are met
        assigned_team = None
        for team, count in team_cr_counts.items():
            if count < target_team_crs:
                assigned_team = team
                team_cr_counts[team] += 1
                break
        if not assigned_team: # If all main teams met target, assign randomly
            assigned_team = random.choice(TEAM_NAMES)


        start_date = generate_random_date(end_date=datetime(2024,3,1))
        num_status_updates = random.randint(1, 3)
        current_state_index = 0
        last_update_date = start_date

        for j in range(num_status_updates):
            if current_state_index >= len(CR_STATES): break
            state = CR_STATES[current_state_index]
            current_state_index += 1

            # Ensure created_at for status update is after or on the last one
            created_at_status = generate_random_date(start_date=last_update_date, end_date=last_update_date + timedelta(days=random.randint(1, 30)))
            last_update_date = created_at_status

            end_date = generate_random_date(start_date=created_at_status, end_date=created_at_status + timedelta(days=random.randint(5, 60)))


            rows.append([
                cr_id_base, title,
                random.choice(generated_jira_ids_unique) if generated_jira_ids_unique and random.random() > 0.5 else "",
                random.choice(generated_confluence_ids) if generated_confluence_ids and random.random() > 0.7 else "",
                state, random.choice(USER_NAMES), assigned_team, random.choice(USER_NAMES),
                random.choice(["Production", "Staging", "Development", "N/A"]),
                generate_semicolon_delimited_list(["Payments", "Mobile Banking", "Security", "Core API", "Marketing"]),
                random.choice(CR_TYPES), random.choice(CR_CATEGORIES), random.choice(CR_RISKS),
                random.randint(0, 100) if random.random() > 0.3 else "",
                random.randint(1, 90), random.choice(["No Conflict", "Conflict Detected", "Resolved"]),
                fake.bs() + " " + fake.bs(),
                start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"),
                "Details in Confluence" if random.random() > 0.5 else fake.sentence(nb_words=6),
                "Standard rollback" if random.random() > 0.5 else fake.sentence(nb_words=5),
                random.choice(USER_NAMES),
                created_at_status.strftime("%Y-%m-%d")
            ])

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"Generated {filename} with {len(rows)} data rows ({num_unique_crs} unique CRs).")


def generate_cr_ctasks_csv(filename="CR_CTasks.csv", num_rows=18):
    header = [
        'CTASK_ID', 'CR_ID', 'CTASK_Assigned_To_User', 'CTASK_Start_Time',
        'CTASK_End_Time', 'CTASK_Description'
    ]
    rows = []
    if not generated_cr_ids:
        print("Cannot generate CR_CTasks.csv: No CR_IDs available.")
        return

    for i in range(num_rows):
        start_time = fake.date_time_between(start_date="-60d", end_date="now")
        rows.append([
            f"CTASK{i+1:03d}", random.choice(generated_cr_ids), random.choice(USER_NAMES),
            start_time.strftime("%Y-%m-%d %H:%M"),
            (start_time + timedelta(hours=random.randint(2, 48))).strftime("%Y-%m-%d %H:%M"),
            fake.catch_phrase()
        ])
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"Generated {filename} with {len(rows)} data rows.")


def generate_jira_issues_detailed_csv(filename="JIRA_Issues_Detailed.csv", num_unique_issues=72):
    global generated_jira_ids_unique
    header = [
        'JIRA_ID', 'JIRA_Type', 'JIRA_Priority', 'JIRA_Components', 'JIRA_Labels',
        'JIRA_Sprint', 'JIRA_App_Name', 'JIRA_Reporter', 'JIRA_Assignee',
        'JIRA_Start_Date', 'JIRA_End_Date', 'JIRA_Status', 'JIRA_Title',
        'JIRA_Description', 'JIRA_Release_Fix_Version', 'JIRA_Team', 'JIRA_Confidence',
        'JIRA_Created_Date', 'JIRA_Updated_Date', 'JIRA_Effort_Story_Points',
        'CR_ID_Link_From_CSV_Example', 'JIRA_Linked_Issue_ID_Target', 'JIRA_Link_Type', 'JIRA_Watcher_User'
    ]
    all_jira_rows = [] # Will store all rows including duplicates for links/watchers
    jira_id_counter = 1

    for i in range(num_unique_issues):
        jira_id_base = f"NOVA-{jira_id_counter:03d}"
        if random.random() < 0.2: # Add some other prefixes
            jira_id_base = f"{random.choice(['LOG','PERF','BUG','FEAT'])}-{jira_id_counter:03d}"

        generated_jira_ids_unique.append(jira_id_base) # Store unique ID
        jira_id_counter += 1

        created_date = generate_random_date(end_date=datetime(2024,4,1))
        start_date = generate_random_date(start_date=created_date, end_date=created_date + timedelta(days=10))
        end_date = generate_random_date(start_date=start_date, end_date=start_date + timedelta(days=random.randint(5,60)))
        updated_date = generate_random_date(start_date=created_date, end_date=end_date if end_date < datetime.now().date() else datetime.now().date() - timedelta(days=1) )


        base_jira_data = [
            jira_id_base, random.choice(JIRA_TYPES), random.choice(JIRA_PRIORITIES),
            generate_semicolon_delimited_list(["API", "Mobile UI", "Database", "Auth", "Payments", "NFC"]),
            generate_semicolon_delimited_list(["performance", "security", "sprint-goal", "ProjectNova", "tech-debt", "ux"]),
            f"Sprint {random.randint(1,5)} - {random.choice(['Nova','General','Infra'])}",
            random.choice(["CoreBankingApp_Wallet", "MobileApp_Global", "AdminPortal", ""]) if random.random() > 0.3 else "",
            random.choice(USER_NAMES), random.choice(USER_NAMES),
            start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"),
            random.choice(JIRA_STATUSES), fake.bs().capitalize(), fake.sentence(nb_words=10),
            f"v{random.randint(0,2)}.{random.randint(1,9)}.{random.randint(0,5)}{random.choice(['-beta','-RC','','-hotfix'])}",
            random.choice(TEAM_NAMES[:3]), # Primary dev teams
            random.randint(50, 100) if random.random() > 0.5 else "",
            created_date.strftime("%Y-%m-%d"), updated_date.strftime("%Y-%m-%d"),
            random.choice([1, 2, 3, 5, 8, 13, 21]) if random.random() > 0.2 else "",
            random.choice(generated_cr_ids) if generated_cr_ids and random.random() > 0.6 else ""
        ]

        # Add base row (no links/watchers specifically set here for this row)
        all_jira_rows.append(base_jira_data + ["", "", ""])


        # Add rows for Links
        num_links = random.randint(0, 2)
        if num_links > 0 and len(generated_jira_ids_unique) > 1: # Need other JIRAs to link to
            linked_targets_for_this_jira = random.sample(
                [jid for jid in generated_jira_ids_unique if jid != jira_id_base],
                min(num_links, len(generated_jira_ids_unique) -1)
            )
            for target_jira_id in linked_targets_for_this_jira:
                link_row = base_jira_data[:] # Create a copy
                link_row.extend([target_jira_id, random.choice(JIRA_LINK_TYPES), ""]) # Add link info, blank watcher
                all_jira_rows.append(link_row)

        # Add rows for Watchers
        num_watchers = random.randint(0, 3)
        if num_watchers > 0:
            for _ in range(num_watchers):
                watcher_row = base_jira_data[:] # Create a copy
                watcher_row.extend(["", "", random.choice(USER_NAMES)]) # Add watcher info, blank links
                all_jira_rows.append(watcher_row)


    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(all_jira_rows)
    print(f"Generated {filename} with {len(all_jira_rows)} data rows ({num_unique_issues} unique JIRA issues).")


def generate_jira_activities_csv(filename="JIRA_Activities.csv", num_rows=35):
    header = [
        'Activity_ID', 'JIRA_ID', 'Activity_Comment', 'Activity_Timestamp', 'Activity_User'
    ]
    rows = []
    if not generated_jira_ids_unique:
        print("Cannot generate JIRA_Activities.csv: No JIRA_IDs available.")
        return

    for i in range(num_rows):
        rows.append([
            f"ACT{i+1:03d}", random.choice(generated_jira_ids_unique),
            random.choice([fake.sentence(nb_words=7), "Status changed to " + random.choice(JIRA_STATUSES), "Comment added."]),
            fake.date_time_between(start_date="-90d", end_date="now").strftime("%Y-%m-%d %H:%M"),
            random.choice(USER_NAMES)
        ])
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"Generated {filename} with {len(rows)} data rows.")


def generate_confluence_pages_detailed_csv(filename="Confluence_Pages_Detailed.csv", num_rows=23):
    global generated_confluence_ids
    header = [
        'Confluence_ID', 'Confluence_Title', 'Confluence_Owner_Member', 'Confluence_Last_Edited_By',
        'Confluence_Space', 'Confluence_Team_Association', 'Confluence_Content_Summary',
        'Confluence_Linked_Jira_ID', 'Confluence_Linked_CR_ID', 'Confluence_Parent_Page_ID',
        'Confluence_Created_Date', 'Confluence_Last_Modified_Date'
    ]
    rows = []
    parent_page_ids = [] # Store some page IDs to be potential parents

    for i in range(num_rows):
        conf_id = f"CONF-{random.choice(['PN','LOG','SEC','ARCH','KB'])}-{i+1:03d}"
        generated_confluence_ids.append(conf_id)
        if random.random() > 0.3: # Some pages are potential parents
            parent_page_ids.append(conf_id)

        created_date = generate_random_date(end_date=datetime(2024,5,1))
        modified_date = generate_random_date(start_date=created_date)

        rows.append([
            conf_id, fake.catch_phrase() + " Documentation", random.choice(USER_NAMES), random.choice(USER_NAMES),
            random.choice(CONFLUENCE_SPACES), random.choice(TEAM_NAMES),
            fake.paragraph(nb_sentences=2),
            generate_semicolon_delimited_list(generated_jira_ids_unique, max_items=4),
            generate_semicolon_delimited_list(generated_cr_ids, max_items=2),
            random.choice(parent_page_ids) if parent_page_ids and random.random() > 0.6 and conf_id not in parent_page_ids else "", # Avoid self-parenting
            created_date.strftime("%Y-%m-%d"), modified_date.strftime("%Y-%m-%d")
        ])
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"Generated {filename} with {len(rows)} data rows.")


# --- Main Generation Call ---
if __name__ == "__main__":
    # Define how many unique items you want for primary entities
    # The JIRA CSV will have more rows due to links/watchers
    # The CR CSV will have more rows due to status updates
    num_unique_crs = 22
    num_unique_jiras = 72
    num_confluence_pages = 23
    num_cr_ctasks = 18
    num_jira_activities = 35

    print("Starting CSV data generation...")

    # Order is important for linking
    generate_jira_issues_detailed_csv(num_unique_issues=num_unique_jiras) # JIRAs first to get IDs
    generate_confluence_pages_detailed_csv(num_rows=num_confluence_pages) # Confluence can link to JIRAs
    generate_cr_main_csv(num_unique_crs=num_unique_crs) # CRs can link to JIRAs & Confluence
    generate_cr_ctasks_csv(num_rows=num_cr_ctasks)
    generate_jira_activities_csv(num_rows=num_jira_activities)

    print("CSV data generation complete.")