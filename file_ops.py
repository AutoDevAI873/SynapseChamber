import os
import logging
import subprocess
import tempfile
import traceback
import json
from datetime import datetime


class FileOperations:
    """
    File operations module providing safe code execution, patch generation,
    and git operations for the Synapse Chamber AutoDev system.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def safe_run_code(self, code_str, timeout=30, dry_run=False):
        """
        Execute Python code safely in a subprocess with timeout.
        
        Args:
            code_str (str): Python code to execute
            timeout (int): Maximum execution time in seconds (default: 30)
            dry_run (bool): If True, validate code without executing (default: False)
            
        Returns:
            dict: {
                "success": bool,
                "output": str,
                "error": str,
                "execution_time": float (optional),
                "dry_run": bool
            }
        """
        try:
            if not code_str or not isinstance(code_str, str):
                return {
                    "success": False,
                    "output": "",
                    "error": "Invalid code string provided",
                    "dry_run": dry_run
                }
            
            if dry_run:
                self.logger.info("Dry run mode: Validating code without execution")
                try:
                    compile(code_str, '<string>', 'exec')
                    return {
                        "success": True,
                        "output": "Code validation successful (dry run)",
                        "error": "",
                        "dry_run": True
                    }
                except SyntaxError as e:
                    return {
                        "success": False,
                        "output": "",
                        "error": f"Syntax error: {str(e)}",
                        "dry_run": True
                    }
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code_str)
                temp_file_path = temp_file.name
            
            try:
                self.logger.debug(f"Executing code in subprocess with {timeout}s timeout")
                start_time = datetime.now()
                
                result = subprocess.run(
                    ['python', temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                success = result.returncode == 0
                
                if success:
                    self.logger.info(f"Code executed successfully in {execution_time:.2f}s")
                else:
                    self.logger.warning(f"Code execution failed with return code {result.returncode}")
                
                return {
                    "success": success,
                    "output": result.stdout,
                    "error": result.stderr if result.stderr else "",
                    "execution_time": execution_time,
                    "dry_run": False,
                    "return_code": result.returncode
                }
                
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except subprocess.TimeoutExpired:
            self.logger.error(f"Code execution timed out after {timeout} seconds")
            return {
                "success": False,
                "output": "",
                "error": f"Execution timed out after {timeout} seconds",
                "dry_run": False
            }
        except Exception as e:
            self.logger.error(f"Error in safe_run_code: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "output": "",
                "error": f"Execution error: {str(e)}",
                "dry_run": dry_run
            }
    
    def generate_patch(self, file_path, patch_hint):
        """
        Analyze file and generate a code patch suggestion based on hint.
        
        Args:
            file_path (str): Path to the file to patch
            patch_hint (str): Description or hint of what needs to be changed
            
        Returns:
            dict: {
                "original": str,
                "proposed": str,
                "confidence": float,
                "file_path": str,
                "patch_type": str,
                "suggestions": list
            }
        """
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"File not found: {file_path}")
                return {
                    "original": "",
                    "proposed": "",
                    "confidence": 0.0,
                    "file_path": file_path,
                    "error": f"File not found: {file_path}"
                }
            
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            if not original_content:
                self.logger.warning(f"File is empty: {file_path}")
                return {
                    "original": "",
                    "proposed": "",
                    "confidence": 0.0,
                    "file_path": file_path,
                    "error": "File is empty"
                }
            
            self.logger.info(f"Analyzing file: {file_path}")
            self.logger.info(f"Patch hint: {patch_hint}")
            
            proposed_content = original_content
            confidence = 0.5
            patch_type = "manual_review_required"
            suggestions = []
            
            hint_lower = patch_hint.lower()
            
            if "import" in hint_lower:
                missing_imports = self._extract_import_names(patch_hint)
                if missing_imports:
                    lines = original_content.split('\n')
                    import_index = 0
                    for i, line in enumerate(lines):
                        if line.strip().startswith('import ') or line.strip().startswith('from '):
                            import_index = i + 1
                    
                    for imp in missing_imports:
                        if imp not in original_content:
                            lines.insert(import_index, imp)
                            import_index += 1
                            suggestions.append(f"Added import: {imp}")
                    
                    proposed_content = '\n'.join(lines)
                    confidence = 0.8
                    patch_type = "import_addition"
            
            elif "remove" in hint_lower or "delete" in hint_lower:
                target = self._extract_removal_target(patch_hint)
                if target:
                    lines = original_content.split('\n')
                    new_lines = []
                    removed_count = 0
                    
                    for line in lines:
                        if target not in line:
                            new_lines.append(line)
                        else:
                            removed_count += 1
                            suggestions.append(f"Removed line: {line.strip()}")
                    
                    if removed_count > 0:
                        proposed_content = '\n'.join(new_lines)
                        confidence = 0.7
                        patch_type = "line_removal"
            
            elif "replace" in hint_lower or "change" in hint_lower:
                parts = self._extract_replacement_parts(patch_hint)
                if parts and len(parts) == 2:
                    old_text, new_text = parts
                    if old_text in original_content:
                        proposed_content = original_content.replace(old_text, new_text)
                        confidence = 0.9
                        patch_type = "text_replacement"
                        suggestions.append(f"Replaced '{old_text}' with '{new_text}'")
                    else:
                        suggestions.append(f"Warning: '{old_text}' not found in file")
            
            elif "add" in hint_lower or "insert" in hint_lower:
                if "function" in hint_lower or "def " in hint_lower:
                    patch_type = "function_addition"
                    confidence = 0.6
                    suggestions.append("Suggested: Add function at appropriate location")
                elif "class" in hint_lower:
                    patch_type = "class_addition"
                    confidence = 0.6
                    suggestions.append("Suggested: Add class definition at appropriate location")
                else:
                    patch_type = "content_addition"
                    confidence = 0.5
                    suggestions.append("Manual review required for content addition")
            
            elif "fix" in hint_lower or "bug" in hint_lower or "error" in hint_lower:
                patch_type = "bug_fix"
                confidence = 0.4
                suggestions.append("Bug fix requires manual code review and testing")
                
                if "indentation" in hint_lower:
                    confidence = 0.7
                    suggestions.append("Check for indentation issues")
                elif "syntax" in hint_lower:
                    confidence = 0.6
                    suggestions.append("Check for syntax errors")
            
            if proposed_content == original_content:
                suggestions.append("No automatic patch could be generated. Manual review required.")
                self.logger.info("No automatic changes made - manual review required")
            else:
                self.logger.info(f"Generated patch with confidence: {confidence}")
            
            return {
                "original": original_content,
                "proposed": proposed_content,
                "confidence": confidence,
                "file_path": file_path,
                "patch_type": patch_type,
                "suggestions": suggestions,
                "patch_hint": patch_hint,
                "changed": proposed_content != original_content
            }
            
        except Exception as e:
            self.logger.error(f"Error generating patch: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "original": "",
                "proposed": "",
                "confidence": 0.0,
                "file_path": file_path,
                "error": f"Patch generation error: {str(e)}"
            }
    
    def git_create_pr(self, branch_name, title, diff_content, dry_run=False):
        """
        Create a git branch, apply diff, and commit changes.
        
        Args:
            branch_name (str): Name for the new branch
            title (str): Commit message title
            diff_content (str): Description of changes or diff content
            dry_run (bool): If True, simulate without executing git commands
            
        Returns:
            dict: {
                "success": bool,
                "branch": str,
                "message": str,
                "commit_hash": str (optional),
                "dry_run": bool
            }
        """
        try:
            if not branch_name or not isinstance(branch_name, str):
                return {
                    "success": False,
                    "branch": "",
                    "message": "Invalid branch name provided",
                    "dry_run": dry_run
                }
            
            branch_name = branch_name.strip().replace(' ', '-')
            
            if not title:
                title = f"Auto-generated PR for {branch_name}"
            
            if dry_run:
                self.logger.info(f"Dry run mode: Would create branch '{branch_name}' with title '{title}'")
                return {
                    "success": True,
                    "branch": branch_name,
                    "message": f"Dry run: Would create branch '{branch_name}' and commit with title '{title}'",
                    "dry_run": True,
                    "simulated_operations": [
                        f"git checkout -b {branch_name}",
                        "git add .",
                        f"git commit -m '{title}'"
                    ]
                }
            
            try:
                result = subprocess.run(
                    ['git', 'status'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode != 0:
                    return {
                        "success": False,
                        "branch": "",
                        "message": "Not a git repository or git is not available",
                        "dry_run": False
                    }
            except Exception as e:
                self.logger.error(f"Git status check failed: {str(e)}")
                return {
                    "success": False,
                    "branch": "",
                    "message": f"Git check failed: {str(e)}",
                    "dry_run": False
                }
            
            self.logger.info(f"Creating git branch: {branch_name}")
            
            result = subprocess.run(
                ['git', 'checkout', '-b', branch_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip()
                if "already exists" in error_msg.lower():
                    self.logger.warning(f"Branch {branch_name} already exists, checking it out")
                    result = subprocess.run(
                        ['git', 'checkout', branch_name],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode != 0:
                        return {
                            "success": False,
                            "branch": branch_name,
                            "message": f"Failed to checkout existing branch: {result.stderr}",
                            "dry_run": False
                        }
                else:
                    return {
                        "success": False,
                        "branch": branch_name,
                        "message": f"Failed to create branch: {error_msg}",
                        "dry_run": False
                    }
            
            self.logger.debug("Adding changes to git")
            result = subprocess.run(
                ['git', 'add', '.'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "branch": branch_name,
                    "message": f"Failed to add changes: {result.stderr}",
                    "dry_run": False
                }
            
            commit_message = f"{title}\n\n{diff_content}" if diff_content else title
            
            self.logger.info(f"Committing changes with message: {title}")
            result = subprocess.run(
                ['git', 'commit', '-m', commit_message],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip()
                if "nothing to commit" in error_msg.lower():
                    return {
                        "success": True,
                        "branch": branch_name,
                        "message": "Branch created but nothing to commit (no changes detected)",
                        "dry_run": False,
                        "warning": "No changes to commit"
                    }
                else:
                    return {
                        "success": False,
                        "branch": branch_name,
                        "message": f"Failed to commit: {error_msg}",
                        "dry_run": False
                    }
            
            commit_hash = None
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                commit_hash = result.stdout.strip()
            
            self.logger.info(f"Successfully created branch and committed changes: {commit_hash}")
            
            return {
                "success": True,
                "branch": branch_name,
                "message": f"Successfully created branch '{branch_name}' and committed changes",
                "commit_hash": commit_hash,
                "dry_run": False,
                "commit_title": title
            }
            
        except subprocess.TimeoutExpired:
            self.logger.error("Git operation timed out")
            return {
                "success": False,
                "branch": branch_name,
                "message": "Git operation timed out",
                "dry_run": dry_run
            }
        except Exception as e:
            self.logger.error(f"Error in git_create_pr: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "branch": branch_name,
                "message": f"Git operation error: {str(e)}",
                "dry_run": dry_run
            }
    
    def _extract_import_names(self, hint):
        """Extract import statements from patch hint"""
        imports = []
        lines = hint.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
        return imports
    
    def _extract_removal_target(self, hint):
        """Extract target string to remove from patch hint"""
        if '"' in hint:
            parts = hint.split('"')
            if len(parts) >= 2:
                return parts[1]
        elif "'" in hint:
            parts = hint.split("'")
            if len(parts) >= 2:
                return parts[1]
        
        words = hint.lower().split()
        if "remove" in words:
            idx = words.index("remove")
            if idx + 1 < len(words):
                return words[idx + 1]
        
        return None
    
    def _extract_replacement_parts(self, hint):
        """Extract old and new text from replacement hint"""
        hint_lower = hint.lower()
        
        if "replace" in hint_lower and "with" in hint_lower:
            try:
                parts = hint.split('"')
                if len(parts) >= 4:
                    return (parts[1], parts[3])
                
                parts = hint.split("'")
                if len(parts) >= 4:
                    return (parts[1], parts[3])
            except Exception:
                pass
        
        return None


def safe_run_code(code_str, timeout=30, dry_run=False):
    """
    Convenience function for safe code execution.
    See FileOperations.safe_run_code for details.
    """
    ops = FileOperations()
    return ops.safe_run_code(code_str, timeout, dry_run)


def generate_patch(file_path, patch_hint):
    """
    Convenience function for patch generation.
    See FileOperations.generate_patch for details.
    """
    ops = FileOperations()
    return ops.generate_patch(file_path, patch_hint)


def git_create_pr(branch_name, title, diff_content, dry_run=False):
    """
    Convenience function for git PR creation.
    See FileOperations.git_create_pr for details.
    """
    ops = FileOperations()
    return ops.git_create_pr(branch_name, title, diff_content, dry_run)
