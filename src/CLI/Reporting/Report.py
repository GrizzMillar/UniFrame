from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT

class Report:
    def __init__(self, date, test_summary, environment_details, execution_details, test_suite_results, framework_id):
        self.date = date
        self.test_summary = test_summary
        self.environment_details = environment_details
        self.execution_details = execution_details
        self.test_suite_results = test_suite_results
        self.framework_id = framework_id

    def getDate(self):
        return self.date
    
    def getTestSummary(self):
        return self.test_summary
    
    def getFrameworkID(self):
        return self.framework_id
    
    def getTestSuiteResults(self):
        return self.test_suite_results
    
    def toString(self):
        report_content = f"Test Report {self.date}\n"
        report_content += f"Test Summary\n"
        report_content += "+++++++++++++\n"
        report_content += f"Number of Test Suites's: {self.test_summary.getNumberOfTestSuites()}\n"
        report_content += f"Number of Test Cases's: {self.test_summary.getNumberOfTestCases()}\n"
        report_content += f"Number of Passes's: {self.test_summary.getPasses()}\n"
        report_content += f"Number of Failure's: {self.test_summary.getFailures()}\n"
        report_content += f"Number of Error's: {self.test_summary.getErrors()}\n"
        report_content += f"Success Rate: {self.test_summary.getSuccessRate()}\n"
        report_content += "\n"
        report_content += f"Test Environment\n"
        report_content += "+++++++++++++++++\n"
        report_content += f"OS Type: {self.environment_details.getOSType()}\n"
        report_content += f"OS Version: {self.environment_details.getOSVersion()}\n"
        report_content += f"IP Address: {self.environment_details.getIPAddress()}\n"
        report_content += f"Test Directory: {self.environment_details.getTestDirectory()}\n"
        report_content += f"Python Version: {self.environment_details.getPythonVersion()}\n"
        report_content += "\n"
        report_content += f"Test Execution Details\n"
        report_content += "+++++++++++++++++++++++\n"
        report_content += f"Test Suite's Executed\n"
        for suite in self.execution_details.getTestSuitesExecuted():
            report_content += f"{suite}\n"
        report_content += f"Start Time: {self.execution_details.getStartTime()}\n"
        report_content += f"End Time: {self.execution_details.getEndTime()}\n"
        report_content + f"Total Time: {self.execution_details.getTotalTime()}\n"
        report_content += f"Test Suite Results\n"
        report_content += "+++++++++++++++++++++++\n"
        for test_suite in self.test_suite_results:
            report_content += f"{test_suite.getTestSuiteName()}\n"
            for result in test_suite.getTestResults():
                report_content += f"Test: {result.test_name}, Status: {result.status}, Errors: {result.error_messages}, Time: {result.execution_time}s\n"
            coverage_results = test_suite.getCoverageResults()
            if len(coverage_results) != 0:
                for coverage_result in coverage_results:
                    report_content += f" Function Coverage: {coverage_result.function_coverage}, Line Coverage: {coverage_result.line_coverage}, Branch Coverage: {coverage_result.branch_coverage}, Covered Functions: {coverage_result.covered_functions}, Uncovered Functions: {coverage_result.uncovered_functions}s\n"
            else:
                report_content += "There were no code coverage results recorded"
        return report_content

    def generatePDFReport(self, file_path):
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("Test Report", styles['Title']))
        elements.append(Spacer(1, 12))

        header_style = ParagraphStyle('test_summary_heading', parent=styles['Heading2'], alignment=TA_LEFT, leftIndent=-40)
        elements.append(Paragraph("Test Summary", header_style))
        summary_data = [["Number of Test Suites", "Number of Test Cases", "Number of Passes", "Number of Failures", "Number of Errors", "Success Rate"]]
        summary_row = [
            Paragraph(str(self.test_summary.getNumberOfTestSuites()), styles['Normal']),
            Paragraph(str(self.test_summary.getNumberOfTestCases()), styles['Normal']),
            Paragraph(str(self.test_summary.getPasses()), styles['Normal']),
            Paragraph(str(self.test_summary.getFailures()), styles['Normal']),
            Paragraph(str(self.test_summary.getErrors()), styles['Normal']),
            Paragraph(f"{self.test_summary.getSuccessRate():.4f}%", styles['Normal'])
        ]
        summary_data.append(summary_row)

        column_widths = [1.5*inch, 1.6*inch, 1.4*inch, 1.4*inch, 1.2*inch, 1.2*inch,]
        summary_table = Table(summary_data, colWidths=column_widths, spaceBefore=20)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('BOX', (0,0), (-1,-1), 2, colors.black),
            ('GRID', (0,0), (-1,-1), 1, colors.black),

        ]))
        elements.append(summary_table)
        
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Test Enviornment", header_style))
        environment_data = [["OS Type", "OS Version", "IP Address", "Test Directory", "Python Version"]]
        environment_row = [
            Paragraph(self.environment_details.getOSType(), styles['Normal']),
            Paragraph(self.environment_details.getOSVersion(), styles['Normal']),
            Paragraph(self.environment_details.getIPAddress(), styles['Normal']),
            Paragraph(self.environment_details.getTestDirectory(), styles['Normal']),
            Paragraph(self.environment_details.getPythonVersion(), styles['Normal'])
        ]
        environment_data.append(environment_row)

        environment_column_widths = [1.6*inch, 1.8*inch, 1.5*inch, 1.7*inch, 1.7*inch, 1.6*inch,]
        environment_table = Table(environment_data, colWidths=environment_column_widths, spaceBefore=20)
        environment_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('BOX', (0,0), (-1,-1), 2, colors.black),
            ('GRID', (0,0), (-1,-1), 1, colors.black),

        ]))
        elements.append(environment_table)

        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Test Execution Details", header_style))
        execution_data = [["Test Suite's Executed",  "Start Time", "End Time", "Total Time"]]
        execution_row = [
            Paragraph(str(self.execution_details.getTestSuitesExecuted()), styles['Normal']),
            Paragraph(self.execution_details.getStartTime(), styles['Normal']),
            Paragraph(self.execution_details.getEndTime(), styles['Normal']),
            Paragraph(f"{self.execution_details.getTotalTime():.4f}s", styles['Normal'])
        ]
        execution_data.append(execution_row)

        execution_column_widths = [2*inch, 2.1*inch, 2.1*inch, 2.1*inch, 2.1*inch, 2*inch,]
        execution_table = Table(execution_data, colWidths=execution_column_widths, spaceBefore=20)
        execution_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('BOX', (0,0), (-1,-1), 2, colors.black),
            ('GRID', (0,0), (-1,-1), 1, colors.black),

        ]))
        elements.append(execution_table)

        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Test Suite Results", header_style))
        for test_suite_result in self.test_suite_results:
            table_suite_data = [["Test Suite Name", "Time", "Passed", "Failed", "Error", "Execution Time"]]
            row = [
                Paragraph(test_suite_result.getTestSuiteName(), styles['Normal']),
                Paragraph(str(test_suite_result.getDate()), styles['Normal']),
                Paragraph(str(test_suite_result.getPassed()), styles['Normal']),
                Paragraph(str(test_suite_result.getFailed()), styles['Normal']),
                Paragraph(str(test_suite_result.getErrors()), styles['Normal']),
                Paragraph(f"{test_suite_result.getExecutionTime():.4f}s", styles['Normal'])
            ]
            table_suite_data.append(row)

            test_suite_table = Table(table_suite_data, colWidths=column_widths, spaceBefore=20)
            test_suite_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('BOX', (0,0), (-1,-1), 2, colors.black),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ]))
            elements.append(test_suite_table)
            
            test_results = test_suite_result.getTestResults()
            table_result_data = [["Test Case Name", "Status", "Errors", "Execution Time"]]
            for result in test_results:
                error_message = 'N/A' if not result.getErrorMessages() else result.getErrorMessages()
                row = [
                    Paragraph(result.getName(), styles['Normal']),
                    Paragraph(result.getStatus(), styles['Normal']),
                    Paragraph(error_message, styles['Normal']),
                    Paragraph(result.getExecutionTime() if result.getExecutionTime() is not None else 'N/A', styles['Normal'])
                ]
                table_result_data.append(row)
            test_result_column_widths = [2*inch, 2.1*inch, 2.1*inch, 2.1*inch, 2.1*inch, 2*inch,]
            test_results_table = Table(table_result_data, colWidths=test_result_column_widths, spaceBefore=20)
            test_results_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('BOX', (0,0), (-1,-1), 2, colors.black),
                ('GRID', (0,0), (-1,-1), 1, colors.black),

            ]))
            elements.append(test_results_table)

            coverage_results = test_suite_result.getCoverageResults()
            if coverage_results is not None:
                coverage_data = [["Function Coverage", "Line Coverage", "Branch Coverage", "Covered Functions", "Uncovered Functions"]]
                for coverage_result in coverage_results:
                    row1 = [
                            Paragraph(f"{coverage_result.getFunctionCoverage():.4f}%", styles['Normal']),
                            Paragraph(f"{coverage_result.getLineCoverage():.4f}%", styles['Normal']),
                            Paragraph(f"{coverage_result.getBranchCoverage():.4f}%", styles['Normal']),
                            Paragraph(str(coverage_result.getCoveredFunctions()), styles['Normal']),
                            Paragraph(str(coverage_result.getUncoveredFunctions()), styles['Normal'])
                        ]
                    coverage_data.append(row1)
                coverage_column_widths = [1.6*inch, 1.6*inch, 1.5*inch, 1.8*inch, 1.8*inch,]
                coverage_table = Table(coverage_data, colWidths=coverage_column_widths, spaceBefore=20)
                coverage_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('BOX', (0,0), (-1,-1), 2, colors.black),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ]))
                elements.append(coverage_table)

        doc.build(elements)
    


