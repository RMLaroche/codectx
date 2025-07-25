"""
Static code analyzer using Tree-sitter for extracting signatures without AI

This module provides unified static analysis for Java, Python, and JavaScript/TypeScript
using Tree-sitter parsers to extract class and method signatures.
"""
import os
from pathlib import Path
from typing import List, Dict, Optional, NamedTuple
from dataclasses import dataclass

import ast

try:
    import tree_sitter
    from tree_sitter_languages import get_language
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False


@dataclass
class CodeSignature:
    """Represents a code signature (class, method, function)"""
    type: str  # 'class', 'method', 'function', 'interface'
    name: str
    signature: str
    parameters: List[str]
    return_type: Optional[str]
    decorators: List[str]
    parent_class: Optional[str]
    line_number: int
    visibility: Optional[str] = None  # 'public', 'private', 'protected'


class StaticAnalyzer:
    """Unified static analyzer using Tree-sitter for multiple languages"""
    
    def __init__(self):
        self.languages = {}
        self.parsers = {}
        self.fallback_mode = False
        
        # Try to initialize tree-sitter parsers
        if TREE_SITTER_AVAILABLE:
            supported_langs = ['python', 'java', 'javascript', 'typescript']
            initialized_count = 0
            
            for lang in supported_langs:
                try:
                    language = get_language(lang)
                    parser = tree_sitter.Parser()
                    parser.set_language(language)
                    
                    self.languages[lang] = language
                    self.parsers[lang] = parser
                    print(f"✓ Initialized {lang} parser successfully")
                    initialized_count += 1
                except Exception as e:
                    print(f"Warning: Could not initialize {lang} parser: {e}")
            
            if initialized_count == 0:
                print("Warning: No tree-sitter parsers initialized, using fallback mode")
                self.fallback_mode = True
        else:
            print("Warning: tree-sitter-languages not available, using fallback mode")
            self.fallback_mode = True
    
    def analyze_file(self, file_path: str, content: str) -> List[CodeSignature]:
        """Extract signatures from any supported language file"""
        language = self._detect_language(file_path)
        if not language:
            return []
        
        # Use fallback mode for Python if tree-sitter isn't working
        if self.fallback_mode or language not in self.parsers:
            if language == 'python':
                return self._analyze_python_with_ast(content)
            else:
                print(f"Warning: No parser available for {language} (fallback not implemented)")
                return []
        
        try:
            tree = self.parsers[language].parse(content.encode('utf-8'))
            return self._extract_signatures(tree, language, content)
        except Exception as e:
            print(f"Warning: Failed to parse {file_path}: {e}")
            # Fallback to AST for Python
            if language == 'python':
                return self._analyze_python_with_ast(content)
            return []
    
    def _detect_language(self, file_path: str) -> Optional[str]:
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        
        extension_map = {
            '.py': 'python',
            '.java': 'java',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
        }
        
        return extension_map.get(ext)
    
    def _extract_signatures(self, tree, language: str, content: str) -> List[CodeSignature]:
        """Extract signatures based on language"""
        content_lines = content.split('\n')
        
        if language == 'python':
            return self._extract_python_signatures(tree, content_lines)
        elif language == 'java':
            return self._extract_java_signatures(tree, content_lines)
        elif language in ['javascript', 'typescript']:
            return self._extract_js_signatures(tree, content_lines)
        
        return []
    
    def _extract_python_signatures(self, tree, content_lines: List[str]) -> List[CodeSignature]:
        """Extract Python class and method signatures"""
        signatures = []
        
        def traverse_node(node, parent_class=None):
            if node.type == 'class_definition':
                # Extract class signature
                class_name = self._get_identifier_text(node, 'name')
                line_num = node.start_point[0] + 1
                
                # Get class signature with inheritance
                class_signature = self._get_python_class_signature(node, content_lines)
                
                signatures.append(CodeSignature(
                    type='class',
                    name=class_name,
                    signature=class_signature,
                    parameters=[],
                    return_type=None,
                    decorators=self._get_python_decorators(node),
                    parent_class=None,
                    line_number=line_num
                ))
                
                # Process methods within the class
                for child in node.children:
                    traverse_node(child, class_name)
            
            elif node.type == 'function_definition':
                func_name = self._get_identifier_text(node, 'name')
                line_num = node.start_point[0] + 1
                
                # Get function signature
                signature = self._get_python_function_signature(node, content_lines)
                parameters = self._get_python_parameters(node)
                return_type = self._get_python_return_type(node)
                
                sig_type = 'method' if parent_class else 'function'
                
                signatures.append(CodeSignature(
                    type=sig_type,
                    name=func_name,
                    signature=signature,
                    parameters=parameters,
                    return_type=return_type,
                    decorators=self._get_python_decorators(node),
                    parent_class=parent_class,
                    line_number=line_num
                ))
            
            # Recursively process children
            for child in node.children:
                traverse_node(child, parent_class)
        
        traverse_node(tree.root_node)
        return signatures
    
    def _extract_java_signatures(self, tree, content_lines: List[str]) -> List[CodeSignature]:
        """Extract Java class and method signatures"""
        signatures = []
        
        def traverse_node(node, parent_class=None):
            if node.type in ['class_declaration', 'interface_declaration']:
                class_name = self._get_identifier_text(node, 'name')
                line_num = node.start_point[0] + 1
                
                signature = self._get_java_class_signature(node, content_lines)
                visibility = self._get_java_visibility(node)
                
                sig_type = 'interface' if node.type == 'interface_declaration' else 'class'
                
                signatures.append(CodeSignature(
                    type=sig_type,
                    name=class_name,
                    signature=signature,
                    parameters=[],
                    return_type=None,
                    decorators=self._get_java_annotations(node),
                    parent_class=None,
                    line_number=line_num,
                    visibility=visibility
                ))
                
                # Process methods within the class
                for child in node.children:
                    traverse_node(child, class_name)
            
            elif node.type == 'method_declaration':
                method_name = self._get_identifier_text(node, 'name')
                line_num = node.start_point[0] + 1
                
                signature = self._get_java_method_signature(node, content_lines)
                parameters = self._get_java_parameters(node)
                return_type = self._get_java_return_type(node)
                visibility = self._get_java_visibility(node)
                
                signatures.append(CodeSignature(
                    type='method',
                    name=method_name,
                    signature=signature,
                    parameters=parameters,
                    return_type=return_type,
                    decorators=self._get_java_annotations(node),
                    parent_class=parent_class,
                    line_number=line_num,
                    visibility=visibility
                ))
            
            # Recursively process children
            for child in node.children:
                traverse_node(child, parent_class)
        
        traverse_node(tree.root_node)
        return signatures
    
    def _extract_js_signatures(self, tree, content_lines: List[str]) -> List[CodeSignature]:
        """Extract JavaScript/TypeScript class and function signatures"""
        signatures = []
        
        def traverse_node(node, parent_class=None):
            if node.type == 'class_declaration':
                class_name = self._get_identifier_text(node, 'name')
                line_num = node.start_point[0] + 1
                
                signature = self._get_js_class_signature(node, content_lines)
                
                signatures.append(CodeSignature(
                    type='class',
                    name=class_name,
                    signature=signature,
                    parameters=[],
                    return_type=None,
                    decorators=[],
                    parent_class=None,
                    line_number=line_num
                ))
                
                # Process methods within the class
                for child in node.children:
                    traverse_node(child, class_name)
            
            elif node.type in ['method_definition', 'function_declaration', 'arrow_function']:
                if node.type == 'method_definition':
                    method_name = self._get_js_method_name(node)
                    sig_type = 'method'
                else:
                    method_name = self._get_identifier_text(node, 'name') if node.type == 'function_declaration' else 'anonymous'
                    sig_type = 'function' if not parent_class else 'method'
                
                line_num = node.start_point[0] + 1
                signature = self._get_js_function_signature(node, content_lines)
                parameters = self._get_js_parameters(node)
                
                signatures.append(CodeSignature(
                    type=sig_type,
                    name=method_name,
                    signature=signature,
                    parameters=parameters,
                    return_type=None,  # Could be enhanced for TypeScript
                    decorators=[],
                    parent_class=parent_class,
                    line_number=line_num
                ))
            
            # Recursively process children
            for child in node.children:
                traverse_node(child, parent_class)
        
        traverse_node(tree.root_node)
        return signatures
    
    # Helper methods for extracting specific parts
    def _get_identifier_text(self, node, field_name: str) -> str:
        """Get text of an identifier field"""
        field_node = node.child_by_field_name(field_name)
        if field_node:
            return field_node.text.decode('utf-8')
        return 'unknown'
    
    def _get_python_class_signature(self, node, content_lines: List[str]) -> str:
        """Get Python class signature with inheritance"""
        start_line = node.start_point[0]
        end_line = min(start_line + 2, len(content_lines))  # Look at first 2 lines max
        
        signature_lines = []
        for i in range(start_line, end_line):
            line = content_lines[i].strip()
            signature_lines.append(line)
            if line.endswith(':'):
                break
        
        return ' '.join(signature_lines)
    
    def _get_python_function_signature(self, node, content_lines: List[str]) -> str:
        """Get Python function signature"""
        start_line = node.start_point[0]
        end_line = min(start_line + 3, len(content_lines))  # Look at first 3 lines max
        
        signature_lines = []
        for i in range(start_line, end_line):
            line = content_lines[i].strip()
            signature_lines.append(line)
            if line.endswith(':'):
                break
        
        return ' '.join(signature_lines)
    
    def _get_python_parameters(self, node) -> List[str]:
        """Extract Python function parameters"""
        params = []
        parameters_node = node.child_by_field_name('parameters')
        if parameters_node:
            for child in parameters_node.children:
                if child.type == 'identifier':
                    params.append(child.text.decode('utf-8'))
        return params
    
    def _get_python_return_type(self, node) -> Optional[str]:
        """Extract Python function return type annotation"""
        return_type_node = node.child_by_field_name('return_type')
        if return_type_node:
            return return_type_node.text.decode('utf-8')
        return None
    
    def _get_python_decorators(self, node) -> List[str]:
        """Extract Python decorators"""
        decorators = []
        for child in node.children:
            if child.type == 'decorator':
                decorators.append(child.text.decode('utf-8'))
        return decorators
    
    def _get_java_class_signature(self, node, content_lines: List[str]) -> str:
        """Get Java class signature"""
        start_line = node.start_point[0]
        line = content_lines[start_line].strip()
        return line
    
    def _get_java_method_signature(self, node, content_lines: List[str]) -> str:
        """Get Java method signature"""
        start_line = node.start_point[0]
        end_line = min(start_line + 2, len(content_lines))
        
        signature_parts = []
        for i in range(start_line, end_line):
            line = content_lines[i].strip()
            signature_parts.append(line)
            if '{' in line:
                break
        
        return ' '.join(signature_parts)
    
    def _get_java_parameters(self, node) -> List[str]:
        """Extract Java method parameters"""
        params = []
        parameters_node = node.child_by_field_name('parameters')
        if parameters_node:
            for child in parameters_node.children:
                if child.type == 'formal_parameter':
                    param_text = child.text.decode('utf-8')
                    params.append(param_text)
        return params
    
    def _get_java_return_type(self, node) -> Optional[str]:
        """Extract Java method return type"""
        type_node = node.child_by_field_name('type')
        if type_node:
            return type_node.text.decode('utf-8')
        return None
    
    def _get_java_visibility(self, node) -> Optional[str]:
        """Extract Java visibility modifier"""
        for child in node.children:
            if child.type == 'modifiers':
                text = child.text.decode('utf-8')
                if 'public' in text:
                    return 'public'
                elif 'private' in text:
                    return 'private'
                elif 'protected' in text:
                    return 'protected'
        return None
    
    def _get_java_annotations(self, node) -> List[str]:
        """Extract Java annotations"""
        annotations = []
        for child in node.children:
            if child.type == 'annotation':
                annotations.append(child.text.decode('utf-8'))
        return annotations
    
    def _get_js_class_signature(self, node, content_lines: List[str]) -> str:
        """Get JavaScript class signature"""
        start_line = node.start_point[0]
        line = content_lines[start_line].strip()
        return line
    
    def _get_js_function_signature(self, node, content_lines: List[str]) -> str:
        """Get JavaScript function signature"""
        start_line = node.start_point[0]
        end_line = min(start_line + 2, len(content_lines))
        
        signature_parts = []
        for i in range(start_line, end_line):
            line = content_lines[i].strip()
            signature_parts.append(line)
            if '{' in line:
                break
        
        return ' '.join(signature_parts)
    
    def _get_js_method_name(self, node) -> str:
        """Get JavaScript method name"""
        name_node = node.child_by_field_name('name')
        if name_node:
            return name_node.text.decode('utf-8')
        return 'unknown'
    
    def _get_js_parameters(self, node) -> List[str]:
        """Extract JavaScript function parameters"""
        params = []
        parameters_node = node.child_by_field_name('parameters')
        if parameters_node:
            for child in parameters_node.children:
                if child.type in ['identifier', 'formal_parameter']:
                    params.append(child.text.decode('utf-8'))
        return params


    def _analyze_python_with_ast(self, content: str) -> List[CodeSignature]:
        """Fallback Python analyzer using built-in AST module"""
        try:
            tree = ast.parse(content)
            signatures = []
            
            class SignatureVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.current_class = None
                    self.signatures = []
                
                def visit_ClassDef(self, node):
                    # Extract class signature
                    class_sig = f"class {node.name}"
                    if node.bases:
                        bases = [ast.unparse(base) for base in node.bases]
                        class_sig += f"({', '.join(bases)})"
                    class_sig += ":"
                    
                    decorators = [f"@{ast.unparse(dec)}" for dec in node.decorator_list]
                    
                    self.signatures.append(CodeSignature(
                        type='class',
                        name=node.name,
                        signature=class_sig,
                        parameters=[],
                        return_type=None,
                        decorators=decorators,
                        parent_class=None,
                        line_number=node.lineno
                    ))
                    
                    # Visit methods within the class
                    old_class = self.current_class
                    self.current_class = node.name
                    self.generic_visit(node)
                    self.current_class = old_class
                
                def visit_FunctionDef(self, node):
                    # Extract function/method signature
                    args = []
                    for arg in node.args.args:
                        arg_str = arg.arg
                        if arg.annotation:
                            arg_str += f": {ast.unparse(arg.annotation)}"
                        args.append(arg_str)
                    
                    sig = f"def {node.name}({', '.join(args)})"
                    if node.returns:
                        sig += f" -> {ast.unparse(node.returns)}"
                    sig += ":"
                    
                    decorators = [f"@{ast.unparse(dec)}" for dec in node.decorator_list]
                    return_type = ast.unparse(node.returns) if node.returns else None
                    
                    sig_type = 'method' if self.current_class else 'function'
                    
                    self.signatures.append(CodeSignature(
                        type=sig_type,
                        name=node.name,
                        signature=sig,
                        parameters=[arg.arg for arg in node.args.args],
                        return_type=return_type,
                        decorators=decorators,
                        parent_class=self.current_class,
                        line_number=node.lineno
                    ))
                    
                    self.generic_visit(node)
                
                def visit_AsyncFunctionDef(self, node):
                    # Handle async functions similarly
                    args = []
                    for arg in node.args.args:
                        arg_str = arg.arg
                        if arg.annotation:
                            arg_str += f": {ast.unparse(arg.annotation)}"
                        args.append(arg_str)
                    
                    sig = f"async def {node.name}({', '.join(args)})"
                    if node.returns:
                        sig += f" -> {ast.unparse(node.returns)}"
                    sig += ":"
                    
                    decorators = [f"@{ast.unparse(dec)}" for dec in node.decorator_list]
                    return_type = ast.unparse(node.returns) if node.returns else None
                    
                    sig_type = 'method' if self.current_class else 'function'
                    
                    self.signatures.append(CodeSignature(
                        type=sig_type,
                        name=node.name,
                        signature=sig,
                        parameters=[arg.arg for arg in node.args.args],
                        return_type=return_type,
                        decorators=decorators,
                        parent_class=self.current_class,
                        line_number=node.lineno
                    ))
                    
                    self.generic_visit(node)
            
            visitor = SignatureVisitor()
            visitor.visit(tree)
            return visitor.signatures
            
        except SyntaxError as e:
            print(f"Warning: Python syntax error: {e}")
            return []
        except Exception as e:
            print(f"Warning: Python AST analysis failed: {e}")
            return []


def format_signatures_output(file_path: str, signatures: List[CodeSignature], checksum: str) -> str:
    """Format signatures into unified markdown output with heritage support"""
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    output = f"## {file_path}\n\n"
    output += f"Analyzed on {timestamp} (checksum: {checksum})\n\n"
    output += "**ANALYSIS MODE**: Signature Analysis\n\n"
    
    if not signatures:
        output += "### Overview\n"
        output += "No code signatures found.\n\n"
        return output
    
    # Group by type
    classes = [s for s in signatures if s.type in ['class', 'interface']]
    methods = [s for s in signatures if s.type == 'method']
    functions = [s for s in signatures if s.type == 'function']
    
    # Add overview section
    output += "### Overview\n"
    overview_items = []
    if classes:
        class_types = {}
        for cls in classes:
            class_types[cls.type] = class_types.get(cls.type, 0) + 1
        
        type_desc = []
        if 'class' in class_types:
            type_desc.append(f"{class_types['class']} class{'es' if class_types['class'] > 1 else ''}")
        if 'interface' in class_types:
            type_desc.append(f"{class_types['interface']} interface{'s' if class_types['interface'] > 1 else ''}")
        overview_items.append(f"**Classes**: {', '.join(type_desc)}")
    
    if functions:
        overview_items.append(f"**Functions**: {len(functions)} global function{'s' if len(functions) > 1 else ''}")
    
    if methods:
        overview_items.append(f"**Methods**: {len(methods)} method{'s' if len(methods) > 1 else ''}")
    
    for item in overview_items:
        output += f"- {item}\n"
    output += "\n"
    
    # Classes section with enhanced formatting
    if classes:
        output += "### Classes\n\n"
        for cls in classes:
            # Class header with type and heritage
            class_type = "Interface" if cls.type == 'interface' else "Class"
            output += f"#### **{cls.name}**\n"
            
            # Code block for signature
            output += "```python\n" if file_path.endswith('.py') else "```java\n" if file_path.endswith('.java') else "```javascript\n"
            output += f"{cls.signature}\n"
            output += "```\n"
            
            # Add heritage information if available
            heritage_info = _extract_heritage_info(cls.signature, cls.type)
            if heritage_info:
                output += f"*{heritage_info}*\n"
            
            # Visibility and decorators
            metadata = []
            if cls.visibility:
                metadata.append(f"Visibility: {cls.visibility}")
            if cls.decorators:
                metadata.append(f"Decorators: {', '.join(cls.decorators)}")
            
            if metadata:
                output += f"- **Metadata**: {' | '.join(metadata)}\n"
            
            # Show methods for this class
            class_methods = [m for m in methods if m.parent_class == cls.name]
            if class_methods:
                output += "\n**Methods:**\n"
                for method in class_methods:
                    visibility_str = f" ({method.visibility})" if method.visibility else ""
                    decorators_str = f" {' '.join(method.decorators)}" if method.decorators else ""
                    
                    # Format method signature properly
                    method_sig = method.signature
                    if method_sig.startswith('def ') or method_sig.startswith('async def '):
                        method_sig = method_sig.replace('def ', '').replace('async def ', '')
                        if method_sig.endswith(':'):
                            method_sig = method_sig[:-1]
                    
                    output += f"- `{decorators_str}{method_sig}`{visibility_str}\n"
            
            output += "\n"
    
    # Functions section
    if functions:
        output += "### Functions\n\n"
        for func in functions:
            # Clean up function signature
            func_sig = func.signature
            if func_sig.startswith('def ') or func_sig.startswith('async def '):
                func_sig = func_sig.replace('def ', '').replace('async def ', '')
                if func_sig.endswith(':'):
                    func_sig = func_sig[:-1]
            
            decorators_str = f"{' '.join(func.decorators)} " if func.decorators else ""
            output += f"- `{decorators_str}{func_sig}`\n"
        
        output += "\n"
    
    return output


def _extract_heritage_info(signature: str, class_type: str) -> str:
    """Extract and format heritage information from class signature"""
    heritage_patterns = {
        # Python: class Child(Parent, Mixin):
        'python': r'class\s+\w+\s*\(([^)]+)\)',
        # Java: class Child extends Parent implements Interface
        'java': r'(?:extends\s+(\w+))|(?:implements\s+([\w,\s]+))',
        # JavaScript: class Child extends Parent
        'javascript': r'class\s+\w+\s+extends\s+(\w+)'
    }
    
    import re
    
    # Detect language from signature patterns
    if signature.startswith('class ') and '(' in signature:
        # Python style
        match = re.search(heritage_patterns['python'], signature)
        if match:
            parents = [p.strip() for p in match.group(1).split(',')]
            if parents and parents[0]:
                return f"Inherits from: {', '.join(parents)}"
    
    elif 'extends' in signature or 'implements' in signature:
        # Java style
        heritage_parts = []
        if 'extends' in signature:
            extends_match = re.search(r'extends\s+(\w+)', signature)
            if extends_match:
                heritage_parts.append(f"Extends: {extends_match.group(1)}")
        
        if 'implements' in signature:
            implements_match = re.search(r'implements\s+([\w,\s]+)', signature)
            if implements_match:
                interfaces = [i.strip() for i in implements_match.group(1).split(',')]
                heritage_parts.append(f"Implements: {', '.join(interfaces)}")
        
        if heritage_parts:
            return ' | '.join(heritage_parts)
    
    elif class_type == 'interface':
        return "Interface definition"
    
    return ""