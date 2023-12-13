from COOL.error import Error
from COOL.nodes.basic_classes import BasicBool, BasicInt, BasicIO, BasicObject, BasicString




class Visitor_Program:

    def __init__(self):
        self.types:dict = {'Object':BasicObject(),'IO':BasicIO()}
        #TODO implement the basic types
        self.basic_types: dict = {
            'Object': BasicObject(), 'IO': BasicIO(), 'Int': BasicInt(), 'String': BasicString(), 'Bool': BasicBool()}

        self.tree = {}# Is the tree of heritance, In each "key" there is a class and its "value" is the class from which it inherits.
        self.errors = []

    def _check_cycle(self, class_:str, node):
        temp_class = class_
        lineage = set()
        lineage.add(class_)
        while temp_class in self.tree.keys():
            if self.types[temp_class].inherits in lineage:
                self.errors.append(Error.error(node.line,node.column,'SemanticError',f'Class {class_}, or an ancestor of {class_}, is involved in an inheritance cycle.'))
                return 
            lineage.add(self.types[temp_class].inherits)
            temp_class = self.tree[temp_class]

    def inheritable_class(self, class_str:str):
        return class_str in self.types.keys()

    def _search_lineage(self,class_:str):
        temp_class = class_
        lineage = []

        while temp_class in self.tree.keys():
            if temp_class in lineage: 
                if temp_class == class_:
                    lineage.pop()
                    return lineage
            inherits_ = self.types[temp_class].inherits
            if inherits_:
                lineage.append(inherits_)
                temp_class = self.tree[temp_class]

            else: break
        return lineage
    
    def _search_attribute_name_in_lineage(self, lineage:list, attrib):
        attrb_equals=[]
        for i in lineage:
            if not i:
                break
            if not self.inheritable_class(i):
                break
            for comprobate_attr in self.types.get(i).attributes:
                if attrib.id == comprobate_attr.id and type(attrib):
                    attrb_equals.append(comprobate_attr)
        return attrb_equals

    def _search_method_name_in_lineage(self, lineage:list, method):
        meths_equals=[]
        for i in lineage:
            if not i:
                break
            if not self.inheritable_class(i):
                break
            for comprobate_meth in self.types.get(i).methods:
                if method.id == comprobate_meth.id:                  
                    meths_equals.append(comprobate_meth)
        return meths_equals
    
    def visit_program(self, node):
        for i in node.classes:
            if  i.type in self.basic_types.keys():
                self.errors.append(Error.error(i.line,i.column,'SemanticError',f'Redefinition of basic class {i.type}.' ))
            elif i.type in self.types.keys():
                self.errors.append(Error.error(i.line,i.column,"SemanticError",'Classes may not be redefined'))
            self.types[i.type] = i

        for cls in node.classes:
            if cls.inherits:
                if not cls.inherits in self.types.keys():
                    if cls.inherits in self.basic_types:
                        self.errors.append(Error.error(cls.line, cls.column, 'SemanticError',
                            f'Class {cls.type} cannot inherit class {cls.inherits}. '))
                    else :
                        self.errors.append(Error.error(cls.line, cls.column, 'TypeError',
                            f'Class {cls.type} inherits from an undefined class {cls.inherits}.'))
                self.tree[cls.type] = cls.inherits
                self._check_cycle(cls.type,cls)

    def _analize_methods(self, features):
        meth_node = set()
        for meth in features:
            if meth.id in meth_node:
                self.errors.append(Error.error(meth.line,meth.column,'SemanticError',f'Method {meth.id} is multiply defined.'))

            if meth.type not in self.types.keys() and not (meth.type in self.basic_types.keys()):
                self.errors.append(Error.error(meth.line,meth.column,'TypeError',f'Undefined return type {meth.type} in method test.'))

            meth_formals_name = set()
            for formal in meth.formals:
                
                if formal.type not in self.types.keys() and not (formal.type in self.basic_types.keys()):
                    self.errors.append(Error.error(meth.line,meth.column,'TypeError',f'Class {formal.type} of formal parameter {formal.id} is undefined.'))
                
                if formal.id in meth_formals_name:
                    self.errors.append(Error.error(meth.line,meth.column,'SemanticError',f'Formal parameter {formal.id} is multiply defined.'))
                meth_formals_name.add(formal.id)
            meth_node.add(meth.id)
        
    def _analize_attributes(self, features):
        attrib_node = set()
        for attrb in features:
            if attrb.id in attrib_node:
                self.errors.append(Error.error(attrb.line,attrb.column,'SemanticError',f'Attribute {attrb.id} is multiply defined in class.'))

            if attrb.type not in self.types.keys() and not (attrb.type in self.basic_types.keys()):
                self.errors.append(Error.error(attrb.line,attrb.column,'TypeError',f'Class {attrb.type} of attribute {attrb.id} is undefined.'))

            attrib_node.add(attrb.id)

    def visit_class(self, node):
        
        self._analize_attributes(node.attributes)
        self._analize_methods(node.methods)

        lineage = self._search_lineage(node.type)

        for attrb in node.attributes:
            equals_attrbs = self._search_attribute_name_in_lineage(lineage,attrb)
            if len(equals_attrbs) > 0:
                self.errors.append(Error.error(attrb.line,attrb.column,'SemanticError',f'Attribute {attrb.id} is an attribute of an inherited class.'))


        for meth in node.methods:
            equals_methods = self._search_method_name_in_lineage(lineage, meth)
            if len(equals_methods) > 0:
                equal_meth = equals_methods[0]
                
                if len(meth.formals) != len(equal_meth.formals):
                    self.errors.append(Error.error(meth.line,meth.column,'SemanticError',f'Incompatible number of formal parameters in redefined method {meth.id}.'))
                    break
                for j in range(len(meth.formals)):
                    if meth.formals[j].type != equal_meth.formals[j].type:
                        self.errors.append(Error.error(meth.line,meth.column,'SemanticError',f'In redefined method {meth.id}, parameter type {meth.formals[j].type} is different from original type {equal_meth.formals[j].type}.'))
                
                if meth.type != equal_meth.type:
                    self.errors.append(Error.error(meth.line,meth.column,'SemanticError',f'In redefined method {meth.id}, return type {meth.type} is different from original return type {equal_meth.type}.'))
            
        
        node.methods_dict = {}
        node.attributes_dict = {}
        node.features_dict = {}
        lineage.append('Object')
        for anc_class in reversed(lineage):
            if not anc_class or not self.inheritable_class(anc_class):
                break
            anc_class = self.types[anc_class]
            
            for attrb in anc_class.attributes:
                node.attributes_dict[attrb.id] = attrb
            for meth in anc_class.methods:
                node.methods_dict[meth.id] = meth
            for feat in anc_class.features:
                node.features_dict[feat.id] = feat
        #TODO check if the methods and attributes are redefined in the dynamic type of the attribute.
        node.methods_dict.update({i.id:i for i in node.methods})
        node.attributes_dict.update({i.id:i for i in node.attributes})
        node.features_dict.update({i.id: i for i in node.features})
        node.lineage = lineage


class Visitor_Class:

    def __init__(self, scope):
        self.scope = scope
        self.errors = []
        self.all_types = scope['all_types']
        self.inheritance_tree = scope['inheritance_tree']  
        self.basic_types =  scope['basic_types']  
        self.type = scope['type']


    def visit_attribute_initialization(self, node):
        attrb = node
        if attrb.id == 'self':
            self.errors.append(Error.error(attrb.line,attrb.column, 'SemanticError', '\'self\' cannot be the name of an attribute.'))
            return None
        if attrb.__dict__.get('expr'):
            attrb_expr = attrb.expr
            type = attrb_expr.check(self)
            if type:
                if attrb.type == type:
                    node.dynamic_type = type
                    return type
                if self.all_types.get(type):
                    lineage = self.all_types[type].lineage
                    if attrb.type not in lineage:
                        self.errors.append(Error.error(attrb.line,attrb.column,'TypeError',f'Inferred type {type} of initialization of attribute {attrb.id} does not conform to declared type {attrb.type}.'))
                        return None
                    else: 
                        node.dynamic_type = type
                        return type
                self.errors.append(Error.error(attrb.line,attrb.column,'TypeError',f'Inferred type {type} of initialization of attribute {attrb.id} does not conform to declared type {attrb.type}.'))
        return None


    def visit_dispatch(self,node):
        if node.type:
            return self.visit_dispatch_type(node)
        if node.expr:                        
            return self.visit_dispatch_expr(node)
        else:
            return self.visit_dispatch_not_expr(node)


    def visit_dispatch_type(self,node):
        if not self.all_types.get(node.type):
            self.errors.append(Error.error(node.line,node.column,'TypeError',f'Dispatch on undefined class {node.type}.'))
            return None
        static_type = node.expr.check(self)
        if not static_type:
            return None
        if not static_type in self.all_types.keys():
            self.errors.append(Error.error(node.line,node.column,'TypeError',f'Dispatch on undefined class {static_type}.'))
            return None
        static_type = self.all_types.get(static_type)
        disp_type = self.all_types.get(node.type)

        if not node.id in static_type.methods_dict.keys() or not node.id in disp_type.methods_dict.keys():
            self.errors.append(Error.error(node.line,node.column,'TypeError',f'Expression type {static_type.type} does not conform to declared static dispatch type {disp_type.type}.'))
            return None
        
        # node.expr = disp_type.type
        # node.type = None
        # return node.check(self)
        import copy
        copy_node = copy.deepcopy(node)
        copy_node.expr = disp_type.type
        copy_node.type = None
        return copy_node.check(self)


    def visit_dispatch_expr(self,node):
        expr_type = node.expr if isinstance(node.expr, str) else node.expr.check(self)
        if expr_type:
            if not expr_type in self.all_types.keys() and not expr_type in self.basic_types.keys():
                #TODO search this error
                self.errors.append(Error.error(node.line,node.column,'TypeError',f'Dispatch on undefined class {expr_type}.'))
                return None
            class_meths = self.all_types[expr_type] if self.all_types.get(expr_type) else self.basic_types.get(expr_type)
            class_meths = class_meths.methods_dict
            if not node.id in class_meths.keys():
                self.errors.append(Error.error(node.line,node.column,'AttributeError',f'Dispatch to undefined method {node.id}.'))
                return None
            elif not len(class_meths[node.id].formals) == len(node.exprs):
                #TODO search this error    
                self.errors.append(Error.error(node.line,node.column,'SemanticError',f'Method {node.id} called with wrong number of arguments.'))
            
            elif len(class_meths[node.id].formals)>0:
                for i, formal in enumerate(class_meths[node.id].formals):
                    type = self.all_types.get(node.exprs[i].check(self))
                    if not type: type = self.temporal_scope.get(node.exprs[i])
                    if not type: type = self.basic_types.get(node.exprs[i].check(self))
                    
                    if not(type.type == formal.type) and not (formal.type in type.lineage):
                        #TODO search this error
                            self.errors.append(Error.error(node.line,node.column,'TypeError',f'In call of method {node.id}, type {type.type} of parameter {formal.id} does not conform to declared type {formal.type}.'))
                            return None
            return class_meths[node.id].type

    def visit_dispatch_not_expr(self,node):
        if not self.scope['methods'].get(node.id):
            self.errors.append(Error.error(node.line,node.column,'AttributeError',f'Dispatch to undefined method {node.id}.'))
            return None
        return self.scope['methods'][node.id].type
        
            
    def visit_method(self, node):
        for i in node.formals:
            if i.id == 'self':
                self.errors.append(Error.error(node.line,node.column,'SemanticError','\'self\' cannot be the name of a formal parameter.'))
                return None
        self.temporal_scope = {i.id:i for i in node.formals}     
        type = node.expr.check(self)        
        self.temporal_scope = {}
        if not type:
            return None
        if  (type not in self.all_types.keys()) and (type not in self.basic_types.keys()):
            self.errors.append(Error.error(node.line,node.column,'TypeError',f'Undefined return type {type} in method {node.id}.'))
            return None
        
        type_lineage = self.all_types[type].lineage if type in self.all_types.keys() else []
        
        if (not (type == node.type) ) and (not (node.type in type_lineage)):
            self.errors.append(Error.error(node.line,node.column,'TypeError',f'Inferred return type {type} of method {node.id} does not conform to declared return type {node.type}.'))
            return None
        
        return type

    def visit_code_block(self, node):
        type = None
        for expr in node.exprs:
            type = expr.check(self)
        return type
    # TODO check if every expr in the method is conform with its type and every formal (variable declaration) is correct

    def search_variable_in_scope(self, exp):
        if self.temporal_scope.get(exp.id):
            return self.temporal_scope.get(exp.id)
        for attr in self.scope['attributes'].values():
            if attr.id == exp.id:
                return attr
        return exp.check(self)


    def visit_operator(self, node):
        ex1 = node.expr1
        ex2 = node.expr2
        type1 = type2 = None

        if not ex1.__dict__.get('id'):
            type1 = ex1.check(self)
        else:
            type1 = self.search_variable_in_scope(ex1)
            if type1 and not isinstance(type1,str):
                type1 = type1.type

        if not ex2.__dict__.get('id'):
            type2 = ex2.check(self)
        else:
            type2 = self.search_variable_in_scope(ex2)
            if type2 and not isinstance(type2,str):
                type2 = type2.type

        if not type1 or not type2:
            self.errors.append(Error.error(node.line,node.column,'TypeError',f'non-{node.return_type} arguments: {type1} {node.symbol} {type2}'))
            return None
        
        possible_types = node.possibles_types
        if  possible_types[0] == 'All':
            possible_types = self.basic_types.keys()
            if not type1 == type2:
                type1_basic = type1 in self.basic_types.keys()
                type2_basic = type2 in self.basic_types.keys()
                if type1_basic and type2_basic:
                    self.errors.append(Error.error(node.line,node.column,'TypeError','Illegal comparison with a basic type.'))
                    return None
                if type1_basic or type2_basic:
                    self.errors.append(Error.error(node.line,node.column,'TypeError','Illegal comparison with a basic type.'))
                    return None                

        elif not (type1 in possible_types and type2 in possible_types):
            self.errors.append(Error.error(node.line,node.column,'TypeError',f'non-{node.return_type} arguments: {type1} {node.symbol} {type2}'))
        return node.return_type
        
    def visit_unary_operator(self, node):
        ex1 = node.expr
        if not ex1.__dict__.get('id'):
            type1 = ex1.check(self)
        else:
            type1 = self.search_variable_in_scope(ex1)
            if type1 and not isinstance(type1,str):
                type1 = type1.type
        
        if not type1:
            self.errors.append(Error.error(node.line,node.column,'TypeError',f'Argument of \'{node.symbol}\' has type {type1} instead of {node.return_type}.'))
            return None
              
        possible_types = node.possibles_types
        if not (type1 in possible_types):
            self.errors.append(Error.error(node.line,node.column,'TypeError',f'Argument of \'{node.symbol}\' has type {type1} instead of {node.return_type}.'))
        return node.return_type

    def visit_new(self, node):
        if not node.type in self.basic_types.keys() and not node.type in self.all_types.keys():
            new_ ='\'new\''
            self.errors.append(Error.error(node.line,node.column,'TypeError',f'{new_} used with undefined class {node.type}.'))
            return None
        return node.type 
    
    def visit_execute_method(self,node):
        self.visit_dispatch_not_expr(node)

    def visit_get_variable(self, node):
        if node.id in self.temporal_scope.keys():
            return self.temporal_scope[node.id].type
        if node.id in self.scope['attributes'].keys():
            return self.scope['attributes'][node.id].type
        else:
            if node.id == 'self':
                return self.scope['type']
            self.errors.append(Error.error(node.line,node.column,'NameError',f'Undeclared identifier {node.id}.'))
            return None

    def visit_let(self, node):
        for i in node.let_list:
            if i.id == 'self':
                self.errors.append(Error.error(node.line,node.column,'SemanticError','\'self\' cannot be bound in a \'let\' expression.'))
                return None
        for i in node.let_list:
            i.check(self)
        self.temporal_scope = {i.id:i for i in node.let_list}     
        type = node.expr.check(self)        
        self.temporal_scope = {}
        if not type:
            return None
        if (type not in self.all_types.keys()) and (type not in self.basic_types.keys()):
            self.errors.append(Error.error(node.line,node.column,'TypeError',f'Undefined return type {type} in method {node.id}.'))
            return None

        return type

    def _search_min_common_type(self, type1, type2):
        lineage1 = [type1.type] + type1.lineage
        lineage2 = [type2.type] + type2.lineage
        for i in lineage1:
            for j in lineage2:
                if i == j:
                    return i
        return 'Object'


    def visit_case_expr(self, node):
        return node.expr.check(self)


    def visit_case(self, node):
        dynamic_type = node.expr.check(self)
        if not dynamic_type or dynamic_type =='void':
            #TODO search this error
            self.errors.append(Error.error(node.line,node.column,'TypeError',f'Case on void.'))
            return None
        cases = node.cases
        return_types = []
        types = []
        for case in cases:
            if case.id == 'self':
                self.errors.append(Error.error(node.line,node.column,'SemanticError','Identifier \'self\' bound in \'case\'.'))
                return None
            
            return_type = case.check(self)
            if not return_type:
                return None            
            return_types.append(return_type)

            type = case.type
            if not type in self.basic_types.keys() and not type in self.all_types.keys():
                self.errors.append(Error.error(case.line,case.column,'TypeError',f'Class {type} of case branch is undefined.'))
                return None
            if type in types:
                self.errors.append(Error.error(case.line,case.column,'SemanticError',f'Duplicate branch {type} in case statement.'))
                return None
            types.append(type)

        comm_type = 'Object'
        for i in range(len(return_types)-1):
            type1 = self.all_types.get(return_types[i]) if return_types[i] in self.all_types.keys() else self.basic_types.get(return_types[i])
            type2 = self.all_types.get(return_types[i+1]) if return_types[i+1] in self.all_types.keys() else self.basic_types.get(return_types[i+1])
            comm_type = self._search_min_common_type(type1,type2)
            return_types[i] = comm_type
        return comm_type
        

    def visit_conditionals(self, node):
        if_expr = node.if_expr.check(self)
        then_expr = node.then_expr.check(self)
        else_expr = node.else_expr.check(self)
        if not if_expr or not then_expr or not else_expr:
            return None
        if not if_expr == 'Bool':
            #TODO search this error
            self.errors.append(Error.error(node.line,node.column,'TypeError',f'Predicate of \'if\' does not have type Bool.'))
            return None
        if then_expr == else_expr:
            return then_expr
        if then_expr in self.basic_types.keys() or else_expr in self.basic_types.keys():
            return 'Object'
        if then_expr in self.all_types.keys() and else_expr in self.all_types.keys():
            then_expr = self.all_types[then_expr]
            else_expr = self.all_types[else_expr]
            return self._search_min_common_type(then_expr,else_expr)
        return 'Object'


    def visit_loops(self, node):
        predicate_type = node.while_expr.check(self)
        body_type = node.loop_expr.check(self)
        if not predicate_type == 'Bool':
            self.errors.append(Error.error(node.line,node.column,'TypeError', 'Loop condition does not have type Bool.'))
        return 'Object'


    def visit_assign(self, node):
        if node.id == 'self':
            self.errors.append(Error.error(node.line,node.column,'SemanticError',f'Cannot assign to \'self\'.'))
            return None
        type = node.expr.check(self)
        if not type:
            return None
        if (not type in self.all_types.keys() )and (not type in self.basic_types.keys()):
            self.errors.append(Error.error(node.line,node.column,'TypeError',f'Undefined return type {type} in method {node.id}.'))
            return None
        
        node.dynamic_type = type
        return type


    def visit_initialization(self, node):
        type = node.expr.check(self)
        if not type:
            return None
        if (not type in self.all_types.keys()) and (not type in self.basic_types.keys()):
            #TODO search this error
            self.errors.append(Error.error(node.line,node.column,'TypeError',f'Undefined return type {type} in method {node.id}.'))
            return None  
              
        type_lineage = self.all_types[type].lineage if type in self.all_types.keys() else []
        if (not (type == node.type) ) and (not (node.type in type_lineage)):
            #TODO search this error
            self.errors.append(Error.error(node.line,node.column,'TypeError',f' Inferred type {type} of initialization of {node.id} does not conform to identifier\'s declared type {node.type}.'))
            return None
        node.dynamic_type = type
        return type


    def visit_declaration(self, node):
        if not node.type in self.all_types.keys() and not node.type in self.basic_types.keys():
            #TODO search this error
            self.errors.append(Error.error(node.line,node.column,'TypeError',f'Class {node.type} of let-bound identifier {node.id} is undefined.'))
            return None
        return node.type


    def visit_self(self, node):
        return self.type

    def visit_isvoid(self, node):
        node.expr.check(self)
        return 'Bool'