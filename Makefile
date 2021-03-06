CXX = g++
CXXFLAGS = -std=c++11
GRAMMAR_OBJS = build/grammar.o build/nonterminal.o build/token.o \
build/production.o
TABLE_OBJS = build/table.o build/lr_table.o build/lalr_table.o \
build/item_set.o build/item.o build/state.o build/item_core.o build/lalr_state.o
CODEGEN_OBJS = build/json_generator.o

all : bin/asparserations

install : all
	cp bin/asparserations ~/local/bin

clean :
	rm build/*
	rm bin/*

build :
	mkdir -p build

bin :
	mkdir -p bin

autogen autogen/include autogen/src :
	mkdir -p autogen && cd autogen && mkdir -p include src

grammar/include/grammar.hpp : grammar/include/nonterminal.hpp \
grammar/include/token.hpp

grammar/include/symbol.hpp : grammar/include/production.hpp

grammar/include/nonterminal.hpp : grammar/include/production.hpp \
				  grammar/include/symbol.hpp

grammar/include/token.hpp : grammar/include/production.hpp \
                            grammar/include/symbol.hpp

table/include/table.hpp: table/include/state.hpp table/include/item.hpp

table/include/lr_table.hpp : table/include/state.hpp table/include/table.hpp

table/include/lalr_table.hpp : table/include/state.hpp table/include/table.hpp

table/include/item_set.hpp : table/include/item.hpp

table/include/lalr_state.hpp : table/include/item_set.hpp

codegen/include/json_generator.hpp : codegen/include/code_generator.hpp

bootstrap/include/lexer.hpp : autogen/include/Parser.hpp

bootstrap/include/callback.hpp : grammar/include/grammar.hpp \
grammar/include/nonterminal.hpp grammar/include/production.hpp

#Grammar
build/grammar.o: grammar/src/grammar.cpp grammar/include/grammar.hpp \
grammar/include/production.hpp| build
	$(CXX) $(CXXFLAGS) -c -o build/grammar.o grammar/src/grammar.cpp

build/nonterminal.o: grammar/src/nonterminal.cpp \
grammar/include/nonterminal.hpp | build
	$(CXX) $(CXXFLAGS) -c -o build/nonterminal.o grammar/src/nonterminal.cpp

build/token.o : grammar/src/token.cpp grammar/include/token.hpp | build
	$(CXX) $(CXXFLAGS) -c -o build/token.o grammar/src/token.cpp

build/production.o : grammar/src/production.cpp grammar/include/production.hpp \
| build
	$(CXX) $(CXXFLAGS) -c -o build/production.o grammar/src/production.cpp

#Table
build/table.o : table/src/table.cpp table/include/table.hpp \
table/include/item_set.hpp grammar/include/token.hpp | build
	$(CXX) $(CXXFLAGS) -c -o build/table.o table/src/table.cpp

build/lr_table.o : table/src/lr_table.cpp grammar/include/grammar.hpp \
grammar/include/nonterminal.hpp grammar/include/token.hpp \
table/include/lr_table.hpp table/include/state.hpp | build
	$(CXX) $(CXXFLAGS) -c -o build/lr_table.o table/src/lr_table.cpp

build/lalr_table.o : table/src/lalr_table.cpp \
table/include/lalr_table.hpp table/include/item_core.hpp \
table/include/item_set.hpp | build
	$(CXX) $(CXXFLAGS) -c -o build/lalr_table.o table/src/lalr_table.cpp

build/item.o : table/src/item.cpp table/include/item.hpp | build
	$(CXX) $(CXXFLAGS) -c -o build/item.o table/src/item.cpp

build/item_set.o : table/src/item_set.cpp table/include/item_set.hpp | build
	$(CXX) $(CXXFLAGS) -c -o build/item_set.o table/src/item_set.cpp

build/state.o : table/src/state.cpp table/include/state.hpp \
grammar/include/production.hpp grammar/include/symbol.hpp | build
	$(CXX) $(CXXFLAGS) -c -o build/state.o table/src/state.cpp

build/item_core.o : table/src/item_core.cpp table/include/item_core.hpp \
grammar/include/production.hpp | build
	$(CXX) $(CXXFLAGS) -c -o build/item_core.o table/src/item_core.cpp

build/lalr_state.o : table/src/lalr_state.cpp table/include/lalr_state.hpp \
| build
	$(CXX) $(CXXFLAGS) -c -o build/lalr_state.o table/src/lalr_state.cpp

#Codegen
build/json_generator.o : codegen/src/json_generator.cpp | build
	$(CXX) $(CXXFLAGS) -c -o build/json_generator.o \
codegen/src/json_generator.cpp

#Miscellaneous
build/grammar_syntax.o : bootstrap/src/grammar_syntax.cpp \
bootstrap/include/grammar_syntax.hpp | build
	$(CXX) $(CXXFLAGS) -c -o build/grammar_syntax.o \
bootstrap/src/grammar_syntax.cpp

build/first_set1.o : tests/src/first_set1.cpp \
bootstrap/include/grammar_syntax.hpp grammar/include/grammar.hpp | build
	$(CXX) $(CXXFLAGS) -c -o build/first_set1.o tests/src/first_set1.cpp

build/print_states.o : tests/src/print_states.cpp \
tests/include/print_states.hpp table/include/state.hpp table/include/table.hpp \
 | build
	$(CXX) $(CXXFLAGS) -c -o build/print_states.o tests/src/print_states.cpp

build/lr_table1.o : tests/src/lr_table1.cpp | build
	$(CXX) $(CXXFLAGS) -c -o build/lr_table1.o tests/src/lr_table1.cpp

build/lalr_table1.o : tests/src/lalr_table1.cpp | build
	$(CXX) $(CXXFLAGS) -c -o build/lalr_table1.o tests/src/lalr_table1.cpp

build/json_test1.o : build tests/src/json_test1.cpp \
codegen/include/json_generator.hpp \
grammar/include/grammar.hpp grammar/include/nonterminal.hpp \
grammar/include/token.hpp table/include/lr_table.hpp
	$(CXX) $(CXXFLAGS) -c -o build/json_test1.o tests/src/json_test1.cpp

build/gen_json.o : bootstrap/src/gen_json.cpp \
codegen/include/json_generator.hpp grammar/include/grammar.hpp \
table/include/lr_table.hpp bootstrap/include/grammar_syntax.hpp | build
	$(CXX) $(CXXFLAGS) -c -o build/gen_json.o bootstrap/src/gen_json.cpp

build/lexer.o : bootstrap/src/lexer.cpp bootstrap/include/lexer.hpp | build
	$(CXX) $(CXXFLAGS) -c -o build/lexer.o bootstrap/src/lexer.cpp

build/parser.o : autogen/src/Parser.cpp autogen/include/Parser.hpp | build
	$(CXX) $(CXXFLAGS) -c -o build/parser.o autogen/src/Parser.cpp

build/callback.o : bootstrap/src/callback.cpp bootstrap/include/callback.hpp \
autogen/include/Parser.hpp | build
	$(CXX) $(CXXFLAGS) -c -o build/callback.o bootstrap/src/callback.cpp

build/main.o : main.cpp autogen/include/Parser.hpp bootstrap/include/lexer.hpp \
bootstrap/include/callback.hpp codegen/include/json_generator.hpp \
grammar/include/grammar.hpp table/include/lr_table.hpp | build
	$(CXX) $(CXXFLAGS) -c -o build/main.o main.cpp

#Executables
bin/first_set1.out : build/first_set1.o build/grammar_syntax.o $(GRAMMAR_OBJS) \
 | bin
	$(CXX) -std=c++11 -o bin/first_set1.out build/first_set1.o \
build/grammar_syntax.o $(GRAMMAR_OBJS)

bin/lr_table1.out : build/lr_table1.o build/print_states.o $(GRAMMAR_OBJS) \
$(TABLE_OBJS) | bin
	$(CXX) -std=c++11 -o bin/lr_table1.out build/lr_table1.o \
build/print_states.o $(GRAMMAR_OBJS) $(TABLE_OBJS)

bin/lalr_table1.out : build/lalr_table1.o build/print_states.o $(GRAMMAR_OBJS) \
$(TABLE_OBJS) | bin
	$(CXX) -std=c++11 -o bin/lalr_table1.out build/lalr_table1.o \
build/print_states.o $(GRAMMAR_OBJS) $(TABLE_OBJS)

bin/json_test1.out : build/json_test1.o $(GRAMMAR_OBJS) $(TABLE_OBJS) \
$(CODEGEN_OBJS) | bin
	$(CXX) -std=c++11 -o bin/json_test1.out build/json_test1.o \
$(GRAMMAR_OBJS) $(TABLE_OBJS) $(CODEGEN_OBJS)

bin/gen_json.out : build/gen_json.o $(GRAMMAR_OBJS) $(TABLE_OBJS) \
$(CODEGEN_OBJS) build/grammar_syntax.o | bin
	$(CXX) -std=c++11 -o bin/gen_json.out build/gen_json.o $(GRAMMAR_OBJS) \
$(TABLE_OBJS) $(CODEGEN_OBJS) build/grammar_syntax.o

bin/asparserations : build/main.o $(GRAMMAR_OBJS) $(TABLE_OBJS) $(CODEGEN_OBJS)\
build/parser.o build/lexer.o build/callback.o | bin
	$(CXX) -std=c++11 -o bin/asparserations build/main.o $(GRAMMAR_OBJS) \
$(TABLE_OBJS) $(CODEGEN_OBJS) build/parser.o build/lexer.o build/callback.o

#Bootstrap
bootstrap/output_json.json : bin/gen_json.out
	bin/gen_json.out > bootstrap/output_json.json

autogen/include/Parser.hpp autogen/src/Parser.cpp : bootstrap/parser_gen.py \
bootstrap/output_json.json bootstrap/config.json | autogen/include autogen/src
	python3 bootstrap/parser_gen.py bootstrap/output_json.json \
	bootstrap/config.json autogen
