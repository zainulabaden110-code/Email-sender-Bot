import yaml
import re

html_content = """<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 650px; margin: 0 auto; border: 1px solid #e5e7eb; border-radius: 12px; overflow: hidden; color: #374151; line-height: 1.6; background-color: #ffffff; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);">
  <!-- Header -->
  <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 40px 30px; text-align: center;">
    <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 800; letter-spacing: -0.5px;">Internship Inquiry</h1>
    <p style="color: #bfdbfe; margin: 10px 0 0 0; font-size: 16px; font-weight: 500;">Data Scientist & Python Developer</p>
  </div>
  
  <!-- Content Body -->
  <div style="padding: 40px 35px;">
    <p style="margin-top: 0; font-size: 16px; color: #111827;">Dear Hiring Team,</p>
    <p>I hope this message finds you well.</p>
    
    <p>My name is <strong>Abdul Rehman Raza</strong>. I am a Data Science undergraduate with 2 years of hands-on experience engineering machine learning architectures, automated pipelines, and full-stack software solutions.</p>
    
    <p>I am reaching out to formally inquire about compensated internship opportunities or junior engineering roles within your organization where I can immediately contribute as a Data Scientist and Python Developer to your data models and deployment pipelines.</p>
    
    <p>Rather than relying purely on academic theory, I have designed, built, and deployed an ecosystem of over 21 data-driven and full-stack projects. Some of my featured engineering work includes:</p>
    
    <div style="background-color: #f8fafc; border-left: 4px solid #3b82f6; padding: 15px 20px; margin: 25px 0;">
      <ul style="margin: 0; padding-left: 15px; color: #475569;">
        <li style="margin-bottom: 10px;"><strong>CryptoGuard-AI:</strong> A multi-page continuous web application integrated with predictive models for automated cryptocurrency portfolio management and transaction risk/scam mitigation.</li>
        <li style="margin-bottom: 10px;"><strong>Automated Donation Transparency Engine:</strong> An optimized relational database (RDBMS) architecture utilizing complex multi-table SQL joins, automated server-side Triggers, and analytical Views.</li>
        <li style="margin-bottom: 10px;"><strong>AI Diagnostic Risk Assessment System:</strong> An interactive healthcare engine built with Python and Streamlit, leveraging serialized Support Vector Machine (SVM) algorithms for low-latency inference.</li>
        <li><strong>Secure Multi-Branch Network Infrastructure:</strong> A simulated enterprise hierarchy featuring logical 802.1Q VLAN trunking, EIGRP wide-area routing, and strict edge Access Control Lists (ACLs).</li>
      </ul>
    </div>

    <h3 style="color: #1e3a8a; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; margin-top: 30px;">My Core Technical Matrix Includes:</h3>
    <ul style="padding-left: 20px; color: #475569;">
      <li style="margin-bottom: 6px;"><strong>Core Programming:</strong> Python, SQL (T-SQL), JavaScript (ES6+), HTML5, CSS3</li>
      <li style="margin-bottom: 6px;"><strong>Data Science & ML Frameworks:</strong> TensorFlow, PyTorch, Scikit-Learn, Pandas, NumPy, Predictive Pipelines, and Statistical Preprocessing</li>
      <li style="margin-bottom: 6px;"><strong>Infrastructure & Database Engineering:</strong> Relational Schema Design, Cisco Packet Tracer, Git/GitHub, and Automation Scripting (Selenium)</li>
      <li><strong>Professional Communities:</strong> Active Member of the Google Developer Program and NVIDIA Developer Community.</li>
    </ul>

    <p style="margin-top: 25px;">I operate comfortably at the intersection of core data engineering and Python development. I adapt rapidly to emerging technologies, write highly maintainable code, and thrive in execution-focused software environments. I am ready to contribute and bring immediate value to your technical teams from day one.</p>

    <div style="text-align: center; margin: 40px 0;">
      <a href="https://abdulrehmanraza03.github.io/My-Portfolio/" style="display: inline-block; background-color: #2563eb; color: #ffffff; padding: 14px 32px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2); transition: all 0.2s;">👉 View My Production Portfolio & Live Projects</a>
    </div>

    <p style="margin-bottom: 30px; font-style: italic; color: #6b7280;">If there is any opportunity to connect—even for a brief technical screening or introductory conversation—I would truly appreciate your time.</p>
    <p>Thank you for your valuable time and consideration.</p>

    <!-- Signature -->
    <div style="padding-top: 25px; border-top: 1px solid #e5e7eb; margin-top: 30px;">
      <p style="margin: 0 0 5px 0; color: #111827; font-size: 18px; font-weight: 700;">Abdul Rehman Raza</p>
      <p style="margin: 0 0 15px 0; color: #3b82f6; font-weight: 500;">Data Scientist & Python Developer</p>
      
      <table role="presentation" border="0" cellpadding="0" cellspacing="0" style="width: 100%;">
        <tr>
          <td style="padding-bottom: 8px;">
            <span style="color: #9ca3af; margin-right: 8px;">WhatsApp/Cell:</span> 
            <a href="https://wa.me/923181678758" style="color: #1f2937; text-decoration: none; font-weight: 500;">+92 318 1678758</a>
          </td>
        </tr>
        <tr>
          <td style="padding-bottom: 8px;">
            <span style="color: #9ca3af; margin-right: 8px;">Email:</span> 
            <a href="mailto:abdulrehmanraza60@gmail.com" style="color: #2563eb; text-decoration: none; font-weight: 500;">abdulrehmanraza60@gmail.com</a>
          </td>
        </tr>
        <tr>
          <td style="padding-bottom: 8px;">
            <span style="color: #9ca3af; margin-right: 8px;">GitHub:</span> 
            <a href="https://github.com/AbdulRehmanRaza03" style="color: #1f2937; text-decoration: none;">github.com/AbdulRehmanRaza03</a>
          </td>
        </tr>
        <tr>
          <td>
            <span style="color: #9ca3af; margin-right: 8px;">LinkedIn:</span> 
            <a href="https://linkedin.com/in/abdul-rehman-raza-7a125b332" style="color: #1f2937; text-decoration: none;">linkedin.com/in/abdul-rehman-raza-7a125b332</a>
          </td>
        </tr>
      </table>
    </div>
  </div>
</div>"""

text_content = """Dear Hiring Team,

I hope this message finds you well.

My name is Abdul Rehman Raza. I am a Data Science undergraduate with 2 years of hands-on experience engineering machine learning architectures, automated pipelines, and full-stack software solutions.

I am reaching out to formally inquire about compensated internship opportunities or junior engineering roles within your organization where I can immediately contribute as a Data Scientist and Python Developer to your data models and deployment pipelines.

Rather than relying purely on academic theory, I have designed, built, and deployed an ecosystem of over 21 data-driven and full-stack projects. Some of my featured engineering work includes:

• CryptoGuard-AI: A multi-page continuous web application integrated with predictive models for automated cryptocurrency portfolio management and transaction risk/scam mitigation.
• Automated Donation Transparency Engine: An optimized relational database (RDBMS) architecture utilizing complex multi-table SQL joins, automated server-side Triggers, and analytical Views.
• AI Diagnostic Risk Assessment System: An interactive healthcare engine built with Python and Streamlit, leveraging serialized Support Vector Machine (SVM) algorithms for low-latency inference.
• Secure Multi-Branch Network Infrastructure: A simulated enterprise hierarchy featuring logical 802.1Q VLAN trunking, EIGRP wide-area routing, and strict edge Access Control Lists (ACLs).

My Core Technical Matrix Includes:
- Core Programming: Python, SQL (T-SQL), JavaScript (ES6+), HTML5, CSS3
- Data Science & ML Frameworks: TensorFlow, PyTorch, Scikit-Learn, Pandas, NumPy, Predictive Pipelines, and Statistical Preprocessing
- Infrastructure & Database Engineering: Relational Schema Design, Cisco Packet Tracer, Git/GitHub, and Automation Scripting (Selenium)
- Professional Communities: Active Member of the Google Developer Program and NVIDIA Developer Community.

I operate comfortably at the intersection of core data engineering and Python development. I adapt rapidly to emerging technologies, write highly maintainable code, and thrive in execution-focused software environments. I am ready to contribute and bring immediate value to your technical teams from day one.

👉 View My Production Portfolio & Live Projects: https://abdulrehmanraza03.github.io/My-Portfolio/

If there is any opportunity to connect—even for a brief technical screening or introductory conversation—I would truly appreciate your time.

Thank you for your valuable time and consideration.

Warm regards,

Abdul Rehman Raza
Data Scientist & Python Developer
WhatsApp/Cell: +92 318 1678758
Email: abdulrehmanraza60@gmail.com
GitHub: https://github.com/AbdulRehmanRaza03
LinkedIn: https://linkedin.com/in/abdul-rehman-raza-7a125b332"""

with open("config.yaml", "r", encoding="utf-8") as f:
    yaml_str = f.read()

html_formatted = chr(10).join([f"        {line}" for line in html_content.split(chr(10))])
text_formatted = chr(10).join([f"        {line}" for line in text_content.split(chr(10))])

new_pitch = f'''    web_dev_pitch:
      subject: "Internship for Data Scientist and Python Developer"
      body_html: |
{html_formatted}
      body: |
{text_formatted}
'''

# Use regex to replace the old web_dev_pitch block
pattern = re.compile(r'    web_dev_pitch:\n      subject:.*?(?=\n    [a-zA-Z0-9_]+:|\n#|\Z)', re.DOTALL)
new_yaml_str = pattern.sub(new_pitch, yaml_str)

with open("config.yaml", "w", encoding="utf-8") as f:
    f.write(new_yaml_str)

print("Successfully updated config.yaml!")
