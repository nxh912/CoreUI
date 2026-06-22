import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=Warning, module="urllib3")
import time,json
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import shutil
import os
from google import genai

# Initialize the client (automatically picks up GEMINI_API_KEY from your environment)
client = genai.Client()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # your Vue dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Directory to save uploaded files
UPLOAD_DIR = "uploaded_files"
if not os.path.exists(UPLOAD_DIR):
    assert(0)
    os.makedirs(UPLOAD_DIR)

mro_prompt0 = '''
    'Medical Coding Instructions\nYou are a medical coder in a hospital.
    Review the clinical scenario and patient case with the information provided. Prioritize information in this order: discharge summary, consultation notes, physician notes, and other clinical notes.

    \nImportant
    Guidelines
    
    1. Do not infer any diagnosis on your own

    2.
    All diagnoses MUST BE DOCUMENTED BY A CLINICIAN

    3. Do not give diagnosis based on lab results or image findings alone

    4.
    For each diagnosis, follow the specific format outlined below

    Required Tasks: provide information from A to N

    1.
    Identify the (A) principal diagnosis and all (B) secondary diagnoses for the admission

    o Do not include past medical history as secondary diagnoses

    o
    If there are no secondary diagnoses, omit them

    o Only include active issues noted during the current admission

    2.
    For each diagnosis, provide the following information using this specific format, , numbering each diagnosis in bold:

    Principle Diagnosis or Secondary
    Diagnosis: [Diagnosis Name]

    â€¢ Principal diagnosis/problem (indicate if it contradicts with clinician chosen principal problem in discharge summary)

    Status:

    1. New diagnosis (yes/no)

    2. Dates cited and source of diagnosis

    3. [Add any case-specific details as required below for injury, infection, cancer, etc.]

    Citation:

    1. Quote directly from the paragraph of supporting information from clinical notes including source documentation, date, and time

    2. Primary source should be discharge summary, if not present cite progress notes

    3. Include associated lab results/information cited in the discharge summary

    4. Indicate whether new or existing condition

    5. List conditions documented as complications or "Cx" during current admission with clinical management

    6. Document any inconclusive, "versus" or "vs" conditions mentioned by clinicians with management

    7. Indicate resolved conditions from the current admission
    with clinical management

    Investigation:

    1. Detailed treatments

    2. Investigation results

    3. [Add any case-specific investigation details as required below]

    Careplan:

    1. Related current clinical care

    2. Clinical management details',

    '3. For injury cases, document:

    1. Mechanism of injury

    2. Place of occurrence

    3. Activity at the time of accident

    4. List all injuries: including head injuries ("HI"), hemorrhage, fracture, dislocation, nerve injury, artery injury, tear, strain, laceration, open wound, contusion, bruise and abrasion

    5. Note if clinician documents head injury as "HI" ',

    '4. For infection cases, document:

    1. Relevant microbiology, histology,
    blood culture, wound culture, and cytology results

    2. Drug resistance status if documented by clinician',

    '5. For current cancer cases, document:

    1. Primary site of cancer

    2. All metastasis sites

    3. Detailed morphology',

    '6. For stroke cases, document:

    1. Mechanism of stroke as documented
    by clinician

    2. All stroke-related deficits

    3. From stroke discharge template, list all conditions based on check marks:

    1. Procedures

    2. Stroke disability

    3. Comorbidities

    4. Stroke
    complications',

    '7. For BMT (bone marrow transplant)/stem cell transplant, document:

    1.
    Indicate if allogeneic or autologous

    2. List all diagnoses from check marks on tick boxes',

    '8. For fall cases, document:

    1. Predisposing conditions

    2. Precipitating conditions

    3. Cause of fall

    4. Related injuries',

    '9. For overdose/poisoning cases/self-inflicted injury, document:

    1. Intent of poisoning

    2. Manifestation

    3. List all injuries caused by self-infliction

    4. Place of occurrence

    5. Activity at the time of accident',

    '10. For cases with death, document:

    1. Diagnosis for cause of
    death (COD)',

    "(C) Diabetes Mellitus Documentation

    Provide comprehensive Diabetes
    Mellitus or Impaired Fasting Glucose/glucose regulation/tolerance information:

    1. Type of DM

    2. ALL DM-related conditions/complications:

    1. Metabolic conditions:

    1. Hypertension

    2. Dyslipidemia

    3. Hyperlipidemia

    4. Obesity

    5. Fatty liver

    6. Hyperinsulinism

    7. Acanthosis nigricans

    2. Microvascular complications:

    1. Retinopathy

    2. Cataract

    3. Nephropathy

    4. AoCKD

    5. CKD and staging

    6. Proteinuria

    7. Neuropathy

    8. Postural hypotension

    9. Diabetic
    dermopathy/dermatitis/cardiomyopathy/erythema

    10. Erectile dysfunction

    11.
    Gastroparesis

    12. Cranial nerve palsy

    13.
    Diabetic amyotrophy

    3. Macrovascular complications:

    1.
    PVD

    2. Gangrene

    3. Previous amputation status

    4.
    Foot-related complications:

    1. Peripheral neuropathy

    2.
    Foot ulcer

    3. Callus/callosity

    4. Pressure
    ulcer

    5. Charcot's arthropathy

    6. Foot/ankle
    deformity

    7. Hallux

    8. Neuropathic edema

    9.
    Osteoarthropathy

    10. Wrist/foot drop

    3.
    Report on hypoglycemia if occurred and give cause

    4. Indicate 'Poor controlled DM' if documented as such (not based on HbA1c alone)

    5.
    Indicate if patient is on long-term/current insulin use

    6. Provide causes of CKD if documented

    Additional
    Required Documentation",

    '(D) Bedside procedures (if documented):

    1. Nasoendoscopy, otoscopy,
    bronchoscopy, TEE

    2. Imaging done with anesthesia

    3.
    Wound stitching, intravitreal injection

    4. PICC/arterial/CVC line insertion

    5.
    Tooth extraction

    6. Blood/blood products transfusion

    7.
    Lumbar puncture

    8. Hemodialysis, peritoneal dialysis

    9.
    Radiation therapy for cancer patients',

    '(E) Medication changes during admission',

    '(F) From Allied Health and Nursing assessments:

    1. Speech therapist:

    1.
    Dysphagia, swallowing difficulties

    2. Dysarthria, dysphasia, aphasia, aphonia

    2.
    Dietitian:

    1. Malnutrition (mild, moderate, severe)

    2.
    Malnourished

    3. Cachexia

    3. Podiatrist:

    1.
    Pressure injuries/ulcers, foot ulcers

    2. Wound/callus/hyperkeratosis debridement

    4.
    LDAs/wound:

    1. Pressure injuries/ulcers with degree

    2.
    Bedsore with degree',

    '(G) Laboratory findings:

    1. Electrolyte imbalances based on normal
    ranges:

    1. Sodium: 134-146 mmol/L

    2. Potassium:
    3.5-5.0 mmol/L

    3. pCO2 Arterial/ABG: 35-46 mmHg

    2.
    Hypoglycemia, folate, vitamin B12 deficiency with treatment

    3. eGFR level from renal panel',

    '(H) Other diagnosis:

    1. Give other conditions diagnosed and documented
    during admission and that are not mentioned in the discharge summary

    2. Do not use discharge summary notes to answer

    3.
    Indicate if it is treated/resolved. Provide the detailed documentation with related clinical management.

    4. Cite the specific information from the text.

    5.
    Provide detailed clinical management and cite the text.

    6. Do not invent diagnoses from lab/imaging results alone',

    "(I) Important status documentation (if present):

    1. Hepatitis
    B/C

    2. HIV/retroviral disease

    3. Isolation
    status

    4. Smoking status

    5. Dementia and
    specific type

    6. If deceased, cause of death

    7.
    Non-compliance to treatment/medication

    8. Alcohol consumption

    9.
    Mobility status: bed bound, wheelchair bound, hemiplegia, diplegia, paraplegia

    10. Neurological conditions: cerebral palsy, cognitive impairment, Parkinson's,
    Alzheimer's, vascular dementia

    11. Transplant status: BM, kidney, liver

    12.
    Ostomy status: tracheostomy, amputation, ileostomy, colostomy, cystostomy",

    "(J) Additional sources to check:

    1. Pathology/cytology/histopathology
    reports

    2. Discharge planning issues:

    1.
    Facility admission waiting

    2. Social problems delaying discharge

    3.
    Radiology findings: pleural effusion, atelectasis, lung collapse, pericardial effusion

    4. Behavioral chart for cognitive impairment, dementia, BPSD

    5.
    Line assessment for IV phlebitis, thrombophlebitis, site infection",

    "(K) Summary of admission events:

    1. Key events relating to diagnosis
    and treatment with exact times in bullet points.",

    "(L) Demographic data:

    1. Full name

    2.
    Age, gender, DOB

    3. Birth weight (newborn)

    4.
    Admission date/time, discharge date

    5. Medical service code (department)

    6.
    Attending and discharge clinicians

    7. Indication if deceased or transferred",

    "(M) Past Medical History (Separate Section)

    1. List all past medical
    conditions.

    2. Indicate which past medical conditions required the following intervention during admission.

    o
    Treatment adjustment and specify.

    o Diagnostic and investigation and specify.

    o
    Increase care during admission and specify.",

    "(N) Consultation Notes

    Provide all impressions/diagnoses with
    related clinical management from consultation notes with citations.

    â€¢ Include specific findings from Ophthalmology consultation notes",

    "Final Notes

    â€¢ Indicate resolved conditions with clinical management

    â€¢
    Document inconclusive or 'versus' conditions with management

    â€¢ Note 'AKI' as acute kidney injury/failure

    â€¢
    For multifactorial conditions, cite all contributing conditions.

    â€¢ For condition is predisposed and precipitate by other factors, provide all those
    documented conditions.

    â€¢ If clinician put sign and symptoms as issue, look for these sign and symptoms are linked with diagnoses.

    â€¢
    For wounds not from injury, look for 'ulcer' documentation.

    â€¢ Note any documentation inconsistencies

    â€¢
    Ensure all relevant information is captured for accurate coding",

    "Ventilation

    Give information about ventilation

    -Type
    of ventilation

    --(Non invasive- CPAP, BiPAP, IPPB, IPPV, NIMV, NIPV, IMV, SIMV, CNPV, HFNC, High Flow NC)

    ---do
    not include ventilation given via nasal cannula

    --(Invasive- all above types of ventilation given via endotracheal tube or tracheostomy tube)

    -Count
    duration of ventilation in total hours and minutes for each type of ventilation (non invasive ventilation and invasive ventilation)

    -Do not include
    gaps in between for calculation of total hours

    Tracheostomy information

    -Indicate
    if tracheostomy was done during admission

    - type of tracheostomy",

    "Line assessment

    From lines assessment table -phlebitis scale >1
    to indicate as IV phlebitis and provide any medication given.

    . provide diagnosis if IV site infection, phlebitis, thrombophlebitis",

    "LDAs/Wound

    Provide diagnosis from LDAs/wound

    .
    pressure injuries, pressure ulcer

    . bedsore with degree",

    "(L) Demographic data:

    1. Full name

    2.
    Age, gender, DOB

    3. Birth weight (newborn)

    4.
    Admission date/time, discharge date

    5. Medical service code (department)

    6.
    Attending and discharge clinicians

    7. Indication if deceased or transferred"

    output the result in JSON format.
]'''

mro_prompt  = '''prompt = [
    'Medical Coding Instructions\nYou are a medical coder in a hospital.
    Review the clinical scenario and patient case with the information provided. Prioritize information in this order: discharge summary, consultation notes, physician notes, and other clinical notes.
    \nImportant
    Guidelines
    1. Do not infer any diagnosis on your own
    2.
    All diagnoses MUST BE DOCUMENTED BY A CLINICIAN
    3. Do not give diagnosis based on lab results or image findings alone
    4.
    For each diagnosis, follow the specific format outlined below
    Required Tasks: provide information from A to N
    1.
    Identify the (A) principal diagnosis and all (B) secondary diagnoses for the admission
    o Do not include past medical history as secondary diagnoses
    o
    If there are no secondary diagnoses, omit them
    o Only include active issues noted during the current admission
    2.
    For each diagnosis, provide the following information using this specific format, , numbering each diagnosis in bold:
    Principle Diagnosis or Secondary
    Diagnosis: [Diagnosis Name]
    â€¢ Principal diagnosis/problem (indicate if it contradicts with clinician chosen principal problem in discharge summary)
    Status:
    1.
    New diagnosis (yes/no)
    2. Dates cited and source of diagnosis
    3.
    [Add any case-specific details as required below for injury, infection, cancer, etc.]
    Citation:
    1.
    Quote directly from the paragraph of supporting information from clinical notes including source documentation, date, and tim.2. Primary source shoul. be discharge summary, if not present cite progress notes
    3. Include associated lab results/information cited in the discharge summary
    4.
    Indicate whether new or existing condition
    5. List conditions documented as complications or "Cx" during current admission with clinical management
    6.
    Document any inconclusive, "versus" or "vs" conditions mentioned by clinicians with management
    7. Indicate resolved conditions from the current admission
    with clinical management
    Investigation:
    1.
    Detailed treatments
    2. Investigation results
    3.
    [Add any case-specific investigation details as required below]
    Careplan:
    1.
    Related current clinical care
    2. Clinical management details',

    '3. For injury cases, document:
    1. Mechanism of injury
    2. Place of occurrence
    3. Activity at the time of accident
    4. List all injuries: including head injuries ("HI"), hemorrhage, fracture, dislocation, nerve injury, artery injury, tear, strain, laceration, open wound, contusion, bruise and abrasion
    5. Note if clinician documents head injury as "HI" ',

    '4. For infection cases, document:
    1. Relevant microbiology, histology,
    blood culture, wound culture, and cytology results
    2. Drug resistance status if documented by clinician',

    '5. For current cancer cases, document:
    1. Primary site of cancer
    2. All metastasis sites
    3. Detailed morphology',

    '6. For stroke cases, document:
    1. Mechanism of stroke as documented
    by clinician
    2. All stroke-related deficits
    3. From stroke discharge template, list all conditions based on check marks:
    1. Procedures
    2. Stroke disability
    3. Comorbidities
    4. Stroke
    complications',

    '7. For BMT (bone marrow transplant)/stem cell transplant, document:
    1. Indicate if allogeneic or autologous
    2. List all diagnoses from check marks on tick boxes',

    '8. For fall cases, document:
    1. Predisposing conditions
    2. Precipitating conditions
    3. Cause of fall
    4. Related injuries',

    '9. For overdose/poisoning cases/self-inflicted injury, document:
    1.
    Intent of poisoning
    2. Manifestation
    3.
    List all injuries caused by self-infliction
    4. Place of occurrence
    5.
    Activity at the time of accident',

    '10. For cases with death, document:
    1. Diagnosis for cause of
    death (COD)',

    "(C) Diabetes Mellitus Documentation
    Provide comprehensive Diabetes
    Mellitus or Impaired Fasting Glucose/glucose regulation/tolerance information:
    1. Type of DM
    2.
    ALL DM-related conditions/complications:
    1. Metabolic conditions:
    1.
    Hypertension
    2. Dyslipidemia
    3. Hyperlipidemia
    4.
    Obesity
    5. Fatty liver
    6. Hyperinsulinism
    7.
    Acanthosis nigricans
    2. Microvascular complications:
    1.
    Retinopathy
    2. Cataract
    3. Nephropathy
    4.
    AoCKD
    5. CKD and staging
    6. Proteinuria
    7.
    Neuropathy
    8. Postural hypotension
    9. Diabetic
    dermopathy/dermatitis/cardiomyopathy/erythema
    10. Erectile dysfunction
    11.
    Gastroparesis
    12. Cranial nerve palsy
    13.
    Diabetic amyotrophy
    3. Macrovascular complications:
    1.
    PVD
    2. Gangrene
    3. Previous amputation status
    4.
    Foot-related complications:
    1. Peripheral neuropathy
    2.
    Foot ulcer
    3. Callus/callosity
    4. Pressure
    ulcer
    5. Charcot's arthropathy
    6. Foot /ankle
    deformity
    7. Hallux
    8. Neuropathic edema
    9.
    Osteoarthropathy
    10. Wrist/foot drop
    3.
    Report on hypoglycemia if occurred and give cause
    4. Indicate 'Poor controlled DM' if documented as such (not based on HbA1c alone)
    5.
    Indicate if patient is on long-term/current insulin use
    6. Provide causes of CKD if documented
    Additional
    Required Documentation",

    '(D) Bedside procedures (if documented):
    1. Nasoendoscopy, otoscopy,
    bronchoscopy, TEE
    2. Imaging done with anesthesia
    3.
    Wound stitching, intravitreal injection
    4. PICC/arterial/CVC line insertion
    5.
    Tooth extraction
    6. Blood/blood products transfusion
    7.
    Lumbar puncture
    8. Hemodialysis, peritoneal dialysis
    9.
    Radiation therapy for cancer patients',

    '(E) Medication changes during admission',

    '(F) From Allied Health and Nursing assessments:
    1. Speech therapist:
    1.
    Dysphagia, swallowing difficulties
    2. Dysarthria, dysphasia, aphasia, aphonia
    2.
    Dietitian:
    1. Malnutrition (mild, moderate, severe)
    2.
    Malnourished
    3. Cachexia
    3. Podiatrist:
    1.
    Pressure injuries/ulcers, foot ulcers
    2. Wound/callus/hyperkeratosis debridement
    4.
    LDAs/wound:
    1. Pressure injuries/ulcers with degree
    2.
    Bedsore with degree',

    '(G) Laboratory findings:
    1. Electrolyte imbalances based on normal
    ranges:
    1. Sodium: 134-146 mmol/L
    2. Potassium:
    3.5-5.0 mmol/L
    3. pCO2 Arterial/ABG: 35-46 mmHg
    2.
    Hypoglycemia, folate, vitamin B12 deficiency with treatment
    3. eGFR level from renal panel',

    '(H) Other diagnosis:
    1. Give other conditions diagnosed and documented
    during admission and that are not mentioned in the discharge summary
    2. Do not use discharge summary notes to answer
    3.
    Indicate if it is treated/resolved. Provide the detailed documentation with related clinical management.
    4. Cite the specific information from the text.
    5.
    Provide detailed clinical management and cite the text.
    6. Do not invent diagnoses from lab/imaging results alone',

    "(I) Important status documentation (if present):
    1. Hepatitis
    B/C
    2. HIV/retroviral disease
    3. Isolation
    status
    4. Smoking status
    5. Dementia and
    specific type
    6. If deceased, cause of death
    7.
    Non-compliance to treatment/medication
    8. Alcohol consumption
    9.
    Mobility status: bed bound, wheelchair bound, hemiplegia, diplegia, paraplegia
    10. Neurological conditions: cerebral palsy, cognitive impairment, Parkinson's,
    Alzheimer's, vascular dementia
    11. Transplant status: BM, kidney, liver
    12.
    Ostomy status: tracheostomy, amputation, ileostomy, colostomy, cystostomy",

    "(J) Additional sources to check:
    1. Pathology/cytology/histopathology
    reports
    2. Discharge planning issues:
    1.
    Facility admission waiting
    2. Social problems delaying discharge
    3.
    Radiology findings: pleural effusion, atelectasis, lung collapse, pericardial effusion
    4. Behavioral chart for cognitive impairment, dementia, BPSD
    5.
    Line assessment for IV phlebitis, thrombophlebitis, site infection",

    "(K) Summary of admission events:
    1. Key events relating to diagnosis
    and treatment with exact times in bullet points.",

    "(L) Demographic data:
    1. Full name
    2.
    Age, gender, DOB
    3. Birth weight (newborn)
    4.
    Admission date/time, discharge date
    5. Medical service code (department)
    6.
    Attending and discharge clinicians
    7. Indication if deceased or transferred",

    "(M) Past Medical History (Separate Section)
    1. List all past medical
    conditions.
    2. Indicate which past medical conditions required the following intervention during admission.
    o
    Treatment adjustment and specify.
    o Diagnostic and investigation and specify.
    o
    Increase care during admission and specify.",

    "(N) Consultation Notes
    Provide all impressions/diagnoses with
    related clinical management from consultation notes with citations.
    â€¢ Include specific findings from Ophthalmology consultation notes",

    "Final Notes
    â€¢ Indicate resolved conditions with clinical management
    â€¢
    Document inconclusive or 'versus' conditions with management
    â€¢ Note 'AKI' as acute kidney injury/failure
    â€¢
    For multifactorial conditions, cite all contributing conditions.
    â€¢ For condition is predisposed and precipitate by other factors, provide all those
    documented conditions.
    â€¢ If clinician put sign and symptoms as issue, look for these sign and symptoms are linked with diagnoses.
    â€¢
    For wounds not from injury, look for 'ulcer' documentation.
    â€¢ Note any documentation inconsistencies
    â€¢
    Ensure all relevant information is captured for accurate coding",

    "Ventilation
    Give information about ventilation
    -Type
    of ventilation
    --(Non invasive- CPAP, BiPAP, IPPB, IPPV, NIMV, NIPV, IMV, SIMV, CNPV, HFNC, High Flow NC)
    ---do
    not include ventilation given via nasal cannula
    --(Invasive- all above types of ventilation given via endotracheal tube or tracheostomy tube)
    -Count
    duration of ventilation in total hours and minutes for each type of ventilation (non invasive ventilation and invasive ventilation)
    -Do not include
    gaps in between for calculation of total hours
    Tracheostomy information
    -Indicate
    if tracheostomy was done during admission
    - type of tracheostomy",

    "Line assessment
    From lines assessment table -phlebitis scale >1
    to indicate as IV phlebitis and provide any medication given.
    . provide diagnosis if IV site infection, phlebitis, thrombophlebitis",

    "LDAs/Wound
    Provide diagnosis from LDAs/wound
    .
    pressure injuries, pressure ulcer
    . bedsore with degree",

    "(L) Demographic data:
    1. Full name
    2.
    Age, gender, DOB
    3. Birth weight (newborn)
    4.
    Admission date/time, discharge date
    5. Medical service code (department)
    6.
    Attending and discharge clinicians
    7. Indication if deceased or transferred"
]
'''

example_json_string = '[{"Executive Summary":{"Case ID":"1511341938","Admission Date":"2011-05-24","Discharge Date":"2011-05-31","Patient Profile":"62-year-old female, Chinese ethnicity, independent in activities of daily living (ADL) and a community ambulant[cite: 6]."},"Clinical Diagnoses":{"Principal Diagnosis":{"Condition":"Neutropenic Sepsis (Low risk)","Status":"Acute presentation; treated and resolved during admission[cite: 6].","Clinical Presentation":"Presented with a 1-day history of fever, productive cough with yellowish sputum for 4–5 days, and chills without rigors[cite: 6]. On examination, the patient was afebrile, alert, comfortable, and non-toxic looking[cite: 6]."},"Secondary Diagnoses":[{"Condition":"Metastatic Right Breast Cancer","Status":"Pre-existing, chronic condition; currently undergoing active palliative therapy[cite: 6].","Oncological Staging Details":"Estrogen receptor-positive (ER+ve) and progesterone receptor-positive (PR+ve) right breast cancer[cite: 6]. Status post wide excision, sentinel lymph node resection, and radiotherapy in 2005[cite: 6]. History of disease recurrence with extensive bone and liver metastases; previously defaulted follow-up and stopped tamoxifen[cite: 6]. Current staging CT (18/04/2011) showed no local tumor recurrence, a largely stable right upper lobe pulmonary nodule, an interval reduction in the size of hepatic hypodensities, and largely stable extensive skeletal metastases[cite: 6]."},{"Condition":"Right Shoulder Pain","Status":"Acute symptom; resolved by discharge[cite: 6].","Clinical Presentation":"Complained of right shoulder pain with mild sternoclavicular (SC) tenderness, but retained full active range of motion with no clinical signs of local infection[cite: 6]."},{"Condition":"Hyponatremia","Status":"Laboratory finding on admission[cite: 6].","Diagnostic Findings":"Serum sodium was low at 128 mmol/L[cite: 6]."},{"Condition":"Anemia","Status":"Laboratory finding on admission[cite: 6].","Diagnostic Findings":"Hemoglobin was low at 8.5 g/dL[cite: 6]."}]},"Inpatient Medical Management & Treatment":{"Bedside Procedures & Monitoring":["Continuous monitoring of vital signs[cite: 6].","Serial monitoring of laboratory parameters, demonstrating an upward trend in the Absolute Neutrophil Count (ANC)[cite: 6]."],"Pharmacotherapy Log":[{"Medication":"Empiric Palliative Chemotherapy","Indication":"Metastatic breast cancer","Action Taken":"Cycle 8 of Gemcitabine and Carboplatin (Gem/carbo) was initiated prior to admission on 18/05/2011[cite: 6]."},{"Medication":"Levofloxacin 500mg OM","Indication":"Treatment for neutropenic sepsis / respiratory tract infection","Action Taken":"Prescribed at discharge for a 5-day course[cite: 6]."},{"Medication":"Symptomatic Medications","Indication":"General comfort and symptom control","Action Taken":"Dispensated upon home discharge[cite: 6]."}],"Laboratory Summary Table":{"Hemoglobin (Hb)":"8.5 g/dL (Low)[cite: 6]","Absolute Neutrophil Count (ANC)":"0.9 x 10^9/L (Low; noted to be on an upward trend during admission)[cite: 6]","Sodium (Na)":"128 mmol/L (Low)[cite: 6]","Potassium (K)":"3.9 mmol/L (Normal)[cite: 6]","Urea":"2.9 mmol/L (Normal)[cite: 6]","Creatinine":"37 µmol/L (Normal)[cite: 6]","Blood Cultures":"No growth after 2 days[cite: 6]","Urine Culture":"No growth[cite: 6]","Chest X-Ray (CXR)":"Surgical clips noted over the right mid-zone (MZ); no active lung lesions seen; normal cardiothoracic size[cite: 6]"}},"Care Transition, Palliative Phase, and Death":{"Discharge Plan & Clinical Status":{"Status at Discharge":"Discharged well and stable back to her home environment[cite: 6].","Outpatient Follow-Up Strategy":"To see clinic (TCU) scheduled with her primary doctor under an old existing appointment slot[cite: 6]. Sputum culture results are to be traced at her outpatient review[cite: 6]."},"Survival Status":"Alive at discharge."}},{"Executive Summary":{"Case ID":"1550281012","Admission Date":"2005-05-19","Discharge Date":"2005-05-20","Patient Profile":"57-year-old female, Chinese ethnicity, presenting for an elective surgical intervention[cite: 6]."},"Clinical Diagnoses":{"Principal Diagnosis":{"Condition":"Invasive Right Breast Carcinoma (Grade 2/3)","Status":"Newly diagnosed condition leading to surgical intervention[cite: 6].","Clinical Presentation":"Patient initially presented on 11/05/2005 with a palpable right breast lump[cite: 6].","Diagnostic Investigations":"Mammogram (MMG) and Ultrasound (U/S) demonstrated a lesion highly suspicious for malignancy; histopathological evaluation confirmed Grade 2/3 invasive carcinoma[cite: 6]."},"Secondary Diagnoses":[]},"Inpatient Medical Management & Treatment":{"Bedside Procedures & Interventions":["Surgical Intervention (19/05/2005): Right wide local excision of breast lump and sentinel lymph node biopsy[cite: 6].","Operative Findings: A 15mm tumor located at 1 oclock position of the right breast; tumor excised with wide clear margins[cite: 6].","Intraoperative Lymph Node Mapping: Sentinel node identified in the right axilla; intraoperative frozen section evaluation was negative for malignancy[cite: 6].","Post-Operative Monitoring: Serial monitoring of vitals, surgical site dressing checks (clean and dry, no hyperaemia or gangrene), and confirmation of no post-operative drain placement[cite: 6]."],"Pharmacotherapy Log":[],"Laboratory Summary Table":{"Post-Operative Vital Signs":"Afebrile; Blood Pressure: 110/70 mmHg; Heart Rate: 65 bpm[cite: 6]","Cardiopulmonary Exam":"S1S2 heard with no murmurs; lungs demonstrated good bilateral air entry, clear fields, and no crepitations[cite: 6]"}},"Care Transition, Palliative Phase, and Death":{"Discharge Plan & Clinical Status":{"Status at Discharge":"Recovered exceptionally well and deemed fit for discharge home on Post-Operative Day 1 (POD 1)[cite: 6].","Outpatient Follow-Up Strategy":["To see clinic (TCU) appointment scheduled with the surgical specialist on 08/06/2005[cite: 6].","Nursing clinic review scheduled with Sister Geraldine on Monday, 23/05/2005[cite: 6]."]},"Survival Status":"Alive at discharge."}},{"Executive Summary":{"Case ID":"1590224913","Admission Date":"2009-03-11","Discharge Date":"2009-03-28","Patient Profile":"60-year-old female, Chinese ethnicity, previously independent in all activities of daily living (ADL) and a community ambulant[cite: 6]."},"Clinical Diagnoses":{"Principal Diagnosis":{"Condition":"Left Pathological Acetabular Fracture secondary to Metastatic Breast Cancer","Status":"Acute structural presentation of a relapsed malignancy; managed surgically[cite: 6].","Clinical Presentation":"Admitted following a fall, presenting with severe left hip pain of 1 month duration and an inability to assess left lower limb motor strength due to localized pain[cite: 6]."},"Secondary Diagnoses":[{"Condition":"Relapsed Metastatic Right Breast Cancer","Status":"Recurrence/progression of a historical disease after treatment default[cite: 6].","Oncological Staging Details":"Originally diagnosed with estrogen receptor-positive (ER+) and progesterone receptor-positive (PR+) right breast ductal carcinoma with focal lobular features[cite: 6]. Status post wide excision and sentinel lymph node resection on 19/05/2005, followed by radiotherapy and hormonal treatment[cite: 6]. The patient self-stopped Tamoxifen in 2007 and defaulted oncology medical follow-up[cite: 6]. Current workup confirmed diffuse and extensive metastatic disease involving the entire axial skeleton, pelvis, and ribs[cite: 6]."},{"Condition":"Acute Post-Hematuric / Post-Operative Anemia","Status":"Acute complication during admission; required blood transfusions[cite: 6].","Diagnostic Findings":"Hemoglobin dropped to a nadir of 6.9 g/dL post-operatively[cite: 6]."},{"Condition":"Biliary Tree Prominence","Status":"Incidental radiological finding requiring further outpatient evaluation[cite: 6].","Diagnostic Findings":"CT abdomen/pelvis demonstrated mild prominence of the biliary tree, indicating a need to rule out underlying biliary obstruction[cite: 6]."},{"Condition":"Hemorrhoids","Status":"Pre-existing historical condition per patient report; noted in evaluation of recent hematochezia[cite: 6]."}]},"Inpatient Medical Management & Treatment":{"Bedside Procedures & Interventions":["Surgical Procedure (19/03/2009): Pelvic tumor resection and pelvic reconstruction[cite: 6].","Intraoperative Findings: Confirmed severe pelvic discontinuity, Type IV pelvic involvement, and extensive acetabular metastases[cite: 6].","Orthopedic Splinting & Mobilization: Placed on a Thomas splint post-operatively; advanced to Partial Weight Bearing (PWB) with a walking frame (WF)[cite: 6].","Blood Product Transfusion: Transfused with a total of 3 pints of Packed Cells (PCT) for severe anemia; successfully corrected post-transfusion hemoglobin from 6.9 g/dL to 8.3 g/dL, and finally up to 8.7 g/dL[cite: 6]."],"Pharmacotherapy Log":[{"Medication":"Prophylactic Clexane (Enoxaparin)","Indication":"Venous thromboembolism prophylaxis following orthopedic tumor surgery","Action Taken":"Initiated upon transfer to orthopedic care[cite: 6]."},{"Medication":"Exemestane 25mg OM","Indication":"Aromatase inhibitor therapy for recurrent ER/PR positive metastatic breast cancer","Action Taken":"Initiated post-operatively for a 1-month duration[cite: 6]."},{"Medication":"IV Zometa (Zoledronic Acid) 4mg","Indication":"Bisphosphonate therapy for diffuse skeletal metastases","Action Taken":"Single dose administered intravenously post-operatively[cite: 6]."}],"Laboratory & Imaging Summary Table":{"Hematology":"Total White Cell Count (TWC): 11.21 x 10^9/L (Slightly elevated); Hemoglobin: 11.8 g/dL (Admission) -> 6.9 g/dL (Post-op nadir) -> 8.7 g/dL (Post-transfusion); Platelets: 249 x 10^9/L[cite: 6]","Coagulation Profile":"PT, INR, and APTT were within normal limits[cite: 6]","Biochemistry & Metabolic Panel":"Sodium: 135 mmol/L; Potassium: 4.2 mmol/L; Urea: 4.8 mmol/L; Creatinine: 53 µmol/L; CO2: 26 mmol/L; Glucose: 7 mmol/L[cite: 6]","Radioisotope Bone Scan (11/03/2009)":"Demonstrated extensive, multiple skeletal metastases throughout the axial skeleton, with vertically aligned foci at the anterior left 5th, 6th, and 7th ribs, likely representing recent trauma[cite: 6]","CT Abdomen/Pelvis (12/03/2009)":"No local recurrence in the right breast; no thoracoabdominal adenopathy, pleural effusion, or ascites; confirmed multiple skeletal metastases and a pathological left acetabular fracture; mild prominence of the biliary tree[cite: 6]","Surgical Bone Biopsy":"Histology from the bone specimen confirmed a metastatic adenocarcinoma with an identical morphology to the primary breast ductal carcinoma excised in 2005, confirming breast origin[cite: 6]"}},"Care Transition, Palliative Phase, and Death":{"Discharge Plan & Clinical Status":{"Status at Discharge":"Discharged well on 28/03/2009 with intact neurovascular status and stable vitals[cite: 6].","Outpatient Follow-Up Strategy":["Orthopedic Oncology Follow-up: Scheduled with Professor [REDACTED-DOCTOR] in 2 weeks[cite: 6].","Medical Oncology Follow-up: Scheduled with Dr. [REDACTED-DOCTOR] in 1 to 2 weeks post-discharge to review pendingเพิ่มเติม biomarker stains (ER/PR, Her2) on the recent bone specimen[cite: 6]."]},"Survival Status":"Alive at discharge."}},{"Executive Summary":{"Case ID":"1512617668C","Admission Date":"2012-10-09","Discharge Date":"2012-10-18","Patient Profile":"64-year-old female, independent in activities of daily living (ADL), presenting with progressive pulmonary symptoms on a background of advanced malignancy[cite: 6]."},"Clinical Diagnoses":{"Principal Diagnosis":{"Condition":"Traumatic Hemothorax and Multiple Rib Fractures","Status":"Acute traumatic presentation superimposing on systemic metastatic disease; managed with intercostal catheter insertion[cite: 6].","Clinical Presentation":"Admitted following an incidental finding on routine staging scans, presenting with progressive exertional dyspnea for 2 weeks (decreased exercise tolerance to 2 bus-stops, orthopnea requiring right lateral decubitus positioning), right lower chest wall pain for 2–3 weeks following local trauma (mechanical, graded 5–8/10), and bilateral pitting lower limb edema to the knees for 3 days[cite: 6]."},"Secondary Diagnoses":[{"Condition":"Metastatic Right Breast Cancer with Pseudocirrhosis","Status":"Progressive oncological disease under multi-line palliative management[cite: 6].","Oncological Staging Details":"Primary ER+/PR+ right breast cancer s/p wide local excision, sentinel node biopsy, and RT in 2005[cite: 6]. Complicated by a left acetabular pathological fracture in 2009 requiring major reconstruction, and development of liver metastases in late 2010[cite: 6]. Completed 8 cycles of Gemcitabine/Carboplatin in early 2011, and 13 cycles of Docetaxel/Fulvestrant from May 2011 to September 2012[cite: 6]. Current CT scan (09/10/12) revealed stable pulmonary nodules, ground-glass changes in the left lower lobe, small volume ascites, extensive skeletal metastases, and nodular hepatic changes consistent with chemotherapy-induced pseudocirrhosis[cite: 6]."}]},"Inpatient Medical Management & Treatment":{"Bedside Procedures & Interventions":["Cardio-Thoracic Surgery (CTVS) Consultation: Evaluated and recommended urgent intervention for the large effusion[cite: 6].","Chest Tube Insertion: CT-guided insertion of a right-sided intercostal chest drain performed without any clinical complications; drain remained in-situ for 5 days with progressive fluid resolution confirmed on serial chest X-rays[cite: 6].","Chest Tube Removal: Removed successfully after 5 days with no post-removal leakage, bleeding, or complications[cite: 6]."],"Pharmacotherapy Log":[{"Medication":"Analgesics","Indication":"Pain management for 4th–7th rib fractures and chest tube pain","Action Taken":"Initiated and maintained with good pain tolerance[cite: 6]."},{"Medication":"Dexamethasone","Indication":"Oncological adjunct / premedication","Action Taken":"Scheduled to begin outpatient therapy on Wednesday, 24/10/12[cite: 6]."},{"Medication":"Docetaxel","Indication":"Palliative chemotherapy","Action Taken":"Next cycle deferred during acute traumatic admission; slot to be booked following outpatient review[cite: 6]."}],"Laboratory Summary Table":{"Hemoglobin (Hb)":"8.6 g/dL on admission (mild drop attributed to hemodilution from active intravenous hydration); stabilized between 10.0–11.2 g/dL throughout the remainder of the stay[cite: 6]","Liver Function Tests (LFTs)":"Unremarkable[cite: 6]","Coagulation Profile":"Normal; no underlying coagulopathy identified[cite: 6]","Pleural Fluid Analysis":"Fluid culture demonstrated no bacterial growth; cytological analysis was negative for malignant cells[cite: 6]","Physical Examination":"Tachypnea (RR 26); stony dullness, absent vocal resonance, and decreased air entry at the right lung base; bilateral lower limb pitting edema to the knees (which spontaneously resolved during the admission)[cite: 6]"}},"Care Transition, Palliative Phase, and Death":{"Discharge Plan & Clinical Status":{"Status at Discharge":"Discharged home with significantly improved respiratory function and well-controlled thoracic pain[cite: 6].","Outpatient Follow-Up Strategy":"Scheduled for review at the To See Clinic (TCU) De Zee on Thursday, 25/10/12, with pre-admission blood tests (FBC, Renal Panel 1, LFTs) ordered on arrival[cite: 6]. Chemotherapy scheduling for her next cycle of Docetaxel to be completed immediately following this outpatient review[cite: 6]."},"Survival Status":"Alive at discharge."}},{"Executive Summary":{"Case ID":"1513168165E","Admission Date":"2013-02-05","Discharge Date":"2013-02-09","Patient Profile":"64-year-old female, independent in activities of daily living (ADL) and home ambulant[cite: 6]."},"Clinical Diagnoses":{"Principal Diagnosis":{"Condition":"Massive Recurrent Right Pleural Effusion","Status":"Acute recurrence of an ongoing malignant/haemoserous effusion; managed with emergent drainage[cite: 6].","Clinical Presentation":"Presented with a 2–3 day history of progressive exertional dyspnea and progressive bilateral lower limb swelling, with the left leg noted to be more erythematous and slightly painful on ambulation[cite: 6]."},"Secondary Diagnoses":[{"Condition":"Metastatic Right Breast Cancer with New Hepatic Metastases","Status":"Disease progression confirmed on inpatient imaging[cite: 6].","Oncological Staging Details":"Advanced breast cancer with known skeletal and previous liver involvement[cite: 6]. Palliative chemotherapy with Docetaxel was last administered on 21/12/2012[cite: 6]. Restaging CT TAP (07/02/2013) demonstrated the interval appearance of suspected new liver metastases, paired with non-specific pulmonary ground-glass opacities[cite: 6]."},{"Condition":"Suspected Pulmonary Infection","Status":"New finding under active evaluation[cite: 6].","Diagnostic Findings":"CT chest findings revealed non-specific ground-glass opacification without septal thickening, heavily favoring an infective etiology over lymphangitis carcinomatosa[cite: 6]."},{"Condition":"Transaminitis","Status":"Acute laboratory finding secondary to hepatic disease progression[cite: 6].","Diagnostic Findings":"Inpatient blood profiles demonstrated significantly elevated liver enzymes[cite: 6]."}]},"Inpatient Medical Management & Treatment":{"Bedside Procedures & Interventions":["Emergency Chest Tube Insertion: A right-sided chest tube was emergently inserted in the Accident & Emergency (A&E) department using the Seldinger technique, achieving immediate drainage of 1.5L of haemoserous fluid[cite: 6].","Pleural Fluid Titration: Total volume drained exceeded 5 liters throughout the admission, resulting in marked symptomatic relief and allowing the patient to maintain 100% oxygen saturation on room air[cite: 6].","Chest Tube Removal: The tube was planned for removal and taken out on 09/02/2013 with an intact tip; an incidental minor trauma to the tube right before extraction caused the final output to appear briefly haemoserous, but no immediate post-removal complications, bleeding, or leaks occurred[cite: 6]."],"Pharmacotherapy Log":[{"Medication":"Supplemental Oxygen Therapy","Indication":"Acute respiratory distress in A&E","Action Taken":"Administered at 2L/min via nasal prongs initially; successfully weaned off to room air following initial drainage[cite: 6]."}],"Laboratory & Imaging Summary Table":{"Pleural Fluid Cytology":"Analysis of the drained fluid revealed no malignant cells[cite: 6]; advanced diagnostic fluid panels were sent following tube removal and remain pending to be traced as an outpatient[cite: 6]","Liver Function Tests":"Demonstrated significantly raised liver enzymes (transaminitis)[cite: 6]","Chest X-Ray (CXR)":"Initial film showed a massive right pleural effusion[cite: 6]; post-drainage repeat film confirmed marked structural improvement of the effusion[cite: 6]","CT Thorax, Abdomen, and Pelvis (07/02/2013)":"Confirmed interval development of new hepatic lesions and non-specific ground-glass opacities in the lungs[cite: 6]"}},"Care Transition, Palliative Phase, and Death":{"Discharge Plan & Clinical Status":{"Status at Discharge":"Discharged alive and symptomatically improved on 09/02/2013 to spend the Chinese New Year (CNY) holidays with her family[cite: 6].","Outpatient Follow-Up Strategy":"An outpatient review was scheduled at the To See Clinic (TCU) with Dr. [REDACTED-DOCTOR] at 10:00 AM[cite: 6]. Pre-clinic blood investigations (FBC, Renal Panel, LFTs) are to be completed on arrival, and pending advanced pleural fluid panels will be traced to discuss future systemic palliative treatment options[cite: 6]."},"Survival Status":"Alive at discharge."}},{"Executive Summary":{"Case ID":"1513180322Z","Admission Date":"2013-02-12","Discharge Date":"2013-02-19 (Date of Death)","Patient Profile":"64-year-old female, Chinese ethnicity, previously home ambulant, presenting with rapid clinical deterioration three days following her prior hospital discharge[cite: 6]."},"Clinical Diagnoses":{"Principal Diagnosis":{"Condition":"Metastatic Breast Cancer","Status":"Advanced terminal malignancy; determined as the True Certified Cause of Death (CCOD)[cite: 6].","Clinical Staging Details":"End-stage ER+/PR+ metastatic breast cancer with progressive skeletal, pleural, and comprehensive hepatic metastases[cite: 6]. Inpatient evaluation demonstrated severe worsening of serum aminases paired with clinical jaundice, indicating acute hepatic failure from progressive tumor burden[cite: 6]."},"Secondary Diagnoses":[{"Condition":"Recurrent Malignant Pleural Effusion with Fistulization","Status":"Severe chronic complication[cite: 6].","Clinical Presentation":"Presented with progressive exertional dyspnea for 1–2 days, severe tachypnea (speaking only in short phrases), and decreased air entry across the entire right hemithorax[cite: 6]. Her previous chest drain site demonstrated mild erythema and a continuous, spontaneous discharge of haemoserous pleural fluid on the ward[cite: 6]."},{"Condition":"Suspected Sepsis","Status":"Acute infectious complication; treated and resolved during the admission[cite: 6].","Diagnostic Findings":"Inpatient blood markers revealed an acutely raised White Cell Count (WCC)[cite: 6]. All subsequent microbiological cultures returned with no growth, and her fevers completely settled[cite: 6]."},{"Condition":"Secondary Hyponatremia","Status":"Metabolic complication[cite: 6].","Diagnostic Findings":"Arterial Blood Gas (ABG) demonstrated a normal systemic lactate with no acute metabolic acidosis; however, a concurrent secondary hyponatremia was confirmed, requiring fluid adjustments[cite: 6]."}]},"Inpatient Medical Management & Treatment":{"Bedside Procedures & Interventions":["Pleural Fluid Management: Due to the spontaneous discharge of haemoserous fluid from the old track, a urostomy bag was connected over the site to safely collect and contain the ongoing drainage[cite: 6].","Hemodynamic Support: Maintained on conservative intravenous fluids for persistent ward hypotension[cite: 6].","Comfort Care and Palliative Care Consultation: formal review by the Palliative Medicine specialist team[cite: 6]. Due to severe biochemical and clinical deterioration, the patient was deemed entirely unfit for any further palliative chemotherapy[cite: 6]. The management goal was transitioned completely to Best Supportive Care (BSC) and aggressive comfort-oriented measures[cite: 6]."],"Pharmacotherapy Log":[{"Medication":"Oral Morphine","Indication":"Symptom control for dyspnea and thoracic discomfort","Action Taken":"Initiated on the ward, providing high-quality symptomatic relief[cite: 6]."},{"Medication":"Ceftriaxone and Metronidazole","Indication":"Empiric antimicrobial coverage for suspected sepsis","Action Taken":"Administered intravenously for a complete 5-day course; successfully ceased on 16/02/2013 after fevers resolved[cite: 6]."}],"Laboratory & Clinical Summary Table":{"Pleural Fluid History":"Recent diagnostic results confirmed an exudative profile; fluid AFB smears were negative, cultures showed no growth, and consecutive cytologies were negative for malignant cells[cite: 6]","Physical Examination":"Tachypneic; BP 96/67 mmHg; mild erythema at the old drain site without fluctuance or purulent induration; pitting edema extending to the right shin and up to the left knee[cite: 6]"}},"Care Transition, Palliative Phase, and Death":{"Discharge Plan & Clinical Status":{"Status at Discharge":"The patient experienced progressive, irreversible physiological decline throughout her admission[cite: 6].","Advance Care Planning":"A consensus was reached between the clinical teams and her family to adopt an exclusive comfort pathway; a formal Do Not Resuscitate (DNR) order was established[cite: 6]."},"Death Record":{"Date and Time of Death":"Confirmed asystolic on 2013-02-19 at 07:55 hours[cite: 6].","Certified Cause of Death (CCOD)":"Metastatic breast cancer[cite: 6].","Family Support":"Formal condolences were offered to the family by the ward medical staff[cite: 6]."},"Survival Status":"Deceased."}}]'

def ai_prompt(mro_prompt, content, attempts=5, ai='gemini'):
    import json
    from google.genai.errors import ServerError

    lasterror = None
    for attempt in range(attempts):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[mro_prompt1, content]
            )
            text = response.text
            if text.startswith("```json"): text = text.replace("```json","")
            if text.endswith("```"):       text = text.replace("```","")

        except ServerError as e:
            lasterror = e
            if attempt < attempts - 1:
                print(f"\n---------\n Gemini overloaded (503). Retrying in 2 seconds... (Attempt {attempt + 1}/{attempts})")
                time.sleep(2)
            else:
                # If it fails all 3 times, re-raise the error to let Method 1 handle it
                raise e
            
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            json_dict = {'error': str(err) }
            print("\n\nERROR:\n", json.dumps(json_dict, indent=2))
            assert(0)
            return json_dict

    json_obj = json.loads( example_json_string)
    pretty_json = json.dumps(json_obj, indent=4)
    print(pretty_json)

    return JSONResponse(
        status_code=201, 
        content= json_obj, 
        headers= {"X-Custom-Header": "Value"}
    )

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    filenames = []
    content=""
    for file in files:
        await file.seek(0)
        filestr = await file.read()
        content=f"{content}\n{filestr}"

    ### SEND TO AI: reportstr with mro_prompt
    #print(f"\n  mro_prompt : {mro_prompt}")
    print(f"\n==>  LINE:989 ==> content : \n{content}")

    json_obj = json.loads( example_json_string)
    pretty_json = json.dumps(json_obj, indent=4)
    print(pretty_json)

    return json_obj
