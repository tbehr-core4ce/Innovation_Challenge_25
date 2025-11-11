# data_validator.py
# Add quality checks and error reporting
class DataValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_case(self, case: Dict) -> bool:
        """Validate a single case record"""
        valid = True
        
        # Check required fields
        if not (-90 <= case['lat'] <= 90):
            self.errors.append(f"Invalid latitude: {case['lat']}")
            valid = False
        
        if not (-180 <= case['lng'] <= 180):
            self.errors.append(f"Invalid longitude: {case['lng']}")
            valid = False
        
        # Check case type
        valid_types = ['human', 'avian', 'dairy', 'environmental']
        if case['caseType'] not in valid_types:
            self.errors.append(f"Invalid case type: {case['caseType']}")
            valid = False
        
        # Check severity
        valid_severities = ['low', 'medium', 'high', 'critical']
        if case['severity'] not in valid_severities:
            self.warnings.append(f"Unknown severity: {case['severity']}, defaulting to 'medium'")
            case['severity'] = 'medium'
        
        return valid
    
    def get_report(self) -> str:
        """Generate validation report"""
        report = f"Validation Report:\n"
        report += f"Errors: {len(self.errors)}\n"
        report += f"Warnings: {len(self.warnings)}\n"
        if self.errors:
            report += "\nErrors:\n" + "\n".join(self.errors)
        if self.warnings:
            report += "\nWarnings:\n" + "\n".join(self.warnings)
        return report