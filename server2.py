import os
import json
import boto3
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Cortex AI Bridge Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ENV_REGION = "ap-southeast-1"  # Singapore
MODEL_ID = "global.anthropic.claude-sonnet-4-6"
MAX_TOKENS = 1000

class PromptRequest(BaseModel):
    instruction: str
    context: str
    temperature: float = 0.7
    max_tokens: int = 500

mro_prompt='''prompt = [
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

    presented the output in JSON format, using headers:
    ['(A) Principal Diagnosis':
        [1. Principal Diagnosis,
         2. Principal diagnosis/problem,
         3. Status:
           [a. New diagnosis,
            b. Dates cited and source,
            c. Case-specific details]
         4. Citation,
         5. Investigation,
         6. Careplan:
         ['a. Related current clinical care',
          'b. Clinical management details'
         ]
        ],
      '(B) Secondary Diagnoses':
        [1. Secondary Diagnosis,
        2. Status:
           [a. New diagnosis,
            b. Dates cited and source,
            c. Case-specific infection details],
        3. Citation:
           [a. Quote,
            b. Primary source,
            c. Associated lab results,
            d. New or existing,
            e. Complications,
            f. Inconclusive/versus,
            g.  Resolved conditions],
        4. Investigation:
           [a. Detailed treatments,
            b. Investigation results]],
        5. Careplan:
           [a. Related care]],
      '(C) Diabetes Mellitus Documentation',
      '(D) Bedside & Invasive Procedures',
      '(E) Medication Changes During Admission',
      '(F) From Allied Health and Nursing Assessments':
       ['1. Speech therapist',
        '2. Dietitian',
        '3. Podiatrist',
        '4. LDAs/wound']
     '(G) Laboratory & Renal Panel Findings',
     '(H) Other Diagnoses (Noted & Treated on Ward)',
     '(I) Important Status Documentation',
     '(J) Additional Sources & Ancillary Findings',
     '(K) Summary of Admission Events',
     '(L) Demographic Data',
     '(M) Past Medical History',
     '(N) Consultation & Interdisciplinary Notes',
     '(O) Cases with Death'
    ]
]'''

def get_prompt(instruction, text):
    return [
        {
            "role": "user",
            "content": [
                {"text": instruction},
                {"text": text},
            ]
        }
    ]

def clean_response(text):
    if text:
        return text.replace("```json", "").replace("```", "").strip()
    return text

def bedrock_converse(instruction, text, temperature):
    # CRITICAL ENVIRONMENT CLEANUP: Pop out conflicting bearer keys before client initiation
    os.environ.pop("AWS_BEARER_TOKEN_BEDROCK", None)

    bedrock_client = boto3.client(
        service_name="bedrock-runtime",
        region_name=ENV_REGION
    )

    #print(f"### Converse api, region : {ENV_REGION}")
    prompt = get_prompt(instruction, text)

    try:
        #print(f"### converse api... PROMPT:\n{prompt}\n")
        response = bedrock_client.converse(
            modelId=MODEL_ID,
            messages=prompt,
            inferenceConfig={
                "maxTokens": MAX_TOKENS,
                "temperature": temperature,
            }
        )
        
        output_text = response["output"]["message"]["content"][0]["text"]
        #print(f"### output_text:\n{output_text}\n")

        return {"result": clean_response(output_text)}
    except Exception as e:
        print(f"Error invoking model: {e}")
        raise HTTPException(status_code=500, detail=f"Bedrock Error: {str(e)}")

@app.post("/api/v1/mro_data", response_model=None)
async def generate_ai_response(data: PromptRequest):
    print(f"PROMPT : \n{mro_prompt}")
    print(f"TEXT : \n{data.context}")
    try:
        str = bedrock_converse(
            instruction=mro_prompt, 
            text=data.context, 
            temperature=data.temperature
        )
        str = str.replace('\\n', '\n').replace('\\t', '\t')

        print(f"bedrock_converse API : \n{str}")

        return str
    except Exception as e:
        print(f"An error occurred: {e}")

 
if __name__ == "__main__":
    import uvicorn
    filename = os.path.basename(__file__)
    print(f"FILE : {filename}")
    uvicorn.run(f"{filename[:-3]}:app", host="0.0.0.0", port=8000, reload=True)
    '''testing
    curl -X POST -H "Content-Type: application/json" "http://127.0.0.1:8000/api/v1/mro_data" -d '{
        "instruction": "you are super coder in health care",
        "context": "list all specialist in medicine",
        "temperature": 0.7
    }'
    '''
