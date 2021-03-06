#!/usr/bin/python3
import argparse
import collections
import json
import string
import sys

header_template = """
#ifndef ASPARSERATIONS_GENERATED_${class_name}_H_
#define ASPARSERATIONS_GENERATED_${class_name}_H_

#include <array>
#include <map>
#include <memory>
#include <set>
#include <utility>
#include <vector>

$header_front

$begin_namespace
enum class Token
{
  $tokens
};

enum class Nonterminal
{
  $nonterminals
};

enum class Production
{
  $productions
};

struct Lexer_State
{
  const char* begin;
  const char* end;
  unsigned int lines;
  const char* last_newline;
};

Lexer_State next(const Lexer_State&);

/**
 */
class Node
{
  public:
    Node(const $payload&, const Lexer_State&);
    Node(const $payload&, std::vector<std::unique_ptr<Node>>);
    const $payload& payload() const;
    const std::vector<std::unique_ptr<Node>>& children() const;
    const Lexer_State& state() const;
    virtual ~Node() = default;
  private:
    $payload m_payload;
    std::vector<std::unique_ptr<Node>> m_children;
    Lexer_State m_state;
};

class $class_name
{
public:
  $class_name();
  std::unique_ptr<Node> parse(const std::string&, $lexer&, $callback&);
  static std::string nonterminal_to_string(Nonterminal);
  static std::string production_to_string(Production);
  virtual ~$class_name() = default;
private:

  struct Mangled_Production
  {
    const Nonterminal nonterminal;
    const Production production;
    unsigned int child_count;
  };

  struct Productions
  {
    Productions();
    $mangled_productions_header
  };

  struct State
  {
    std::map<Token,std::pair<const State*,std::set<const Mangled_Production*>>>
      actions;
    std::map<Nonterminal,const State*> gotos;
  };

  std::vector<State> m_states;
  std::vector<std::pair<std::unique_ptr<Node>,const State*>> m_stack;
  std::unique_ptr<Productions> m_productions;
  void m_process(const State&, const Lexer_State&, $lexer&, $callback&, std::unique_ptr<Node>&);
  void m_reduce(const Mangled_Production&, $callback&, std::unique_ptr<Node>&);
};
$end_namespace

#endif
"""

src_template = """
#include <algorithm>
#include <stdexcept>
#include <utility>
#include "../include/$class_name.hpp"
$src_front

$namespace::Lexer_State $namespace::next(const $namespace::Lexer_State& ls)
{
  $namespace::Lexer_State ls_prime = {
    ls.end,
    ls.end,
    ls.lines,
    ls.last_newline
  };
  return ls_prime;
}

$namespace::Node::Node(const $payload& payload,
                       const $namespace::Lexer_State& state)
  : m_payload(payload), m_state(state) {}

$namespace::Node::Node(const $payload& payload,
                       std::vector<std::unique_ptr<Node>> children)
{
  if(children.empty())
    throw std::runtime_error("Zero children,"
                             "call Node(const char*, const char*) instead");
  m_payload = payload;
  m_children = std::move(children);
  m_state = $namespace::Lexer_State {
    m_children.front()->state().begin,
    m_children.back()->state().end,
    m_children.back()->state().lines,
    m_children.back()->state().last_newline
  };
}

const $payload& $namespace::Node::payload() const
{
  return m_payload;
}

const std::vector<std::unique_ptr<$namespace::Node>>&
$namespace::Node::children() const
{
  return m_children;
}

const $namespace::Lexer_State& $namespace::Node::state() const
{
  return m_state;
}

$namespace::$class_name::Productions::Productions()
  : $mangled_productions_src
{
}

$namespace::$class_name::$class_name()
  : m_productions(new Productions()), m_states($state_count)
{
  $states
}

std::unique_ptr<$namespace::Node>
$namespace::$class_name::parse(const std::string& input,
                               $lexer& lexer,
                               $callback& callback)
{
  std::unique_ptr<Node> root;
  m_process(m_states.front(),
            $namespace::Lexer_State{input.data(), input.data(),
                                    1, input.data() - 1},
            lexer, callback, root);
  while(!m_stack.empty()) {
    m_process(*m_stack.back().second,
              $namespace::next(m_stack.back().first->state()),
              lexer, callback, root);
  }
  return root;
}

std::string
$namespace::$class_name::nonterminal_to_string($namespace::Nonterminal nt)
{
  switch(nt) {
    $nonterminals_to_strings
  }
  throw std::runtime_error("Unknown nonterminal");
}

std::string
$namespace::$class_name::production_to_string($namespace::Production p)
{
  switch(p) {
    $productions_to_strings
  }
  throw std::runtime_error("Unknown production");
}

void $namespace::$class_name::m_process(
  const $namespace::$class_name::State& state,
  const $namespace::Lexer_State& lex_state,
  $lexer& lexer,
  $callback& callback,
  std::unique_ptr<$namespace::Node>& root)
{
  $namespace::Lexer_State err;
  for(auto& action : state.actions) {
    auto result = lexer.expect(action.first, lex_state);
    err = result.first;
    if(result.second) {
      if(action.second.first != nullptr) {
        try {
          m_stack.emplace_back(
            std::unique_ptr<$namespace::Node>(new Node(callback.call(action.first,
                                     std::string(result.first.begin,
                                                 result.first.end)),
                     result.first)),
            action.second.first
          );
        } catch(std::runtime_error& e) {
          throw std::runtime_error(std::to_string(err.lines) + ":"
            + std::to_string(err.end - 1 - err.last_newline) + ": " + e.what());
        }
        return;
      }
      if(!action.second.second.empty()) {
        m_reduce(**action.second.second.begin(), callback, root);
        return;
      }
    }
  }
  throw std::runtime_error("Failed parse: " + std::to_string(err.lines)
    + ":" + std::to_string(err.end - err.last_newline));
}

void $namespace::$class_name::m_reduce(
  const $namespace::$class_name::Mangled_Production& production,
  $callback& callback,
  std::unique_ptr<$namespace::Node>& root)
{
  if(m_stack.empty()) throw std::runtime_error("Can't reduce empty stack");
  std::unique_ptr<$namespace::Node> node = nullptr;
  if(production.child_count == 0) {
    node = std::unique_ptr<$namespace::Node>(new Node(callback.call(production.nonterminal,
                                  production.production,
                                  {}),
                    $namespace::next(m_stack.back().first->state())));
  } else {
    std::vector<std::unique_ptr<Node>> popped;
    for(int i = 0; i < production.child_count; ++i) {
      if(m_stack.empty()) throw std::runtime_error("Stack underflow");
      popped.push_back(std::move(m_stack.back().first));
      m_stack.pop_back();
    }
    std::reverse(popped.begin(), popped.end());
    try {
      auto temp = callback.call(production.nonterminal, production.production, popped);
      node = std::unique_ptr<$namespace::Node>(new Node(temp, std::move(popped)));
    } catch(std::runtime_error& e) {
      throw std::runtime_error(std::string("Error: ") + e.what());
    }
  }
  if(production.nonterminal == Nonterminal::accept_) {
    root = std::move(node);
    return;
  }
  const State* state;
  if(m_stack.empty()) {
    state = &m_states[0];
  } else {
    state = m_stack.back().second;
  }
  auto iter = state->gotos.find(production.nonterminal);
  if(iter == m_stack.back().second->gotos.end()) {
    throw std::runtime_error("Unknown nonterminal");
  }
  m_stack.emplace_back(std::move(node), iter->second);
}

"""

def gen_namespace_decls(namespaces):
    begin = ""
    end = ""
    for namespace in namespaces:
        begin += "namespace " + namespace + " {\n"
        end = "} // " + namespace + "\n" + end
    return {"begin_namespace" : begin, "end_namespace" : end}

def gen_production_list(grammar):
    names = set()
    for name,productions in grammar["nonterminals"].items():
        for prodname,wildcard in productions.items():
            names.add(prodname)
    lines = ",\n  ".join(names)
    return lines

def gen_mangled_production_list_header(grammar):
    lines = ""
    for name,productions in grammar["nonterminals"].items():
        for prodname,symbols in productions.items():
            lines += "Mangled_Production " + name + "_" + prodname + ";\n    "
    return lines

def gen_header(template, table, config):
    tokens = ",\n  ".join(table["grammar"]["tokens"])
    nonterminal_list = []
    for name, wildcard in table["grammar"]["nonterminals"].items():
        nonterminal_list.append(name)
    nonterminals = ",\n  ".join(nonterminal_list)
    mangled_productions = gen_mangled_production_list_header(table["grammar"])
    productions = gen_production_list(table["grammar"])
    # Lost in stupid parentheses
    return string.Template( \
             string.Template( \
               string.Template(template) \
               .safe_substitute(config)) \
             .safe_substitute(tokens=tokens, nonterminals=nonterminals, \
                              mangled_productions_header=mangled_productions, \
                              productions=productions,
                              state_count=str(len(table["table"])))) \
           .substitute(gen_namespace_decls(config["namespace"]))

def gen_namespace_prefix(namespaces):
    return "::".join(namespaces)

def gen_mangled_productions_src(grammar):
    lines = []
    for name,productions in grammar["nonterminals"].items():
        for prodname,symbols in productions.items():
            lines.append(name + "_" + prodname + " {Nonterminal::"\
                         + name + ", " + "Production::" + prodname + ", " \
                         + str(len(symbols)) + "}")
    return ",\n  ".join(lines)

def gen_state(template, state, config):
    actions = []
    gotos = []
    for token, action in state["actions"].items():
        action_str = "{\n        Token::" + token + ", {"
        if action["shift"] is None:
            action_str += "nullptr, {\n          "
        else:
            action_str += "&m_states["+str(action["shift"])+"], {\n          "
        reduce_strs = map(lambda x :
                          "&m_productions->" + x["nonterminal"]
                          + "_" + x["production"],\
                          action["reductions"])
        reduce_str = ",\n          ".join(reduce_strs)
        action_str += reduce_str + "\n        }}\n      }"
        actions.append(action_str)
    for nonterminal, index in state["gotos"].items():
        goto_str = "{Nonterminal::" + nonterminal \
                   + ", &m_states[" + str(index) + "]}"
        gotos.append(goto_str)

    actions_str = ",\n      ".join(actions)
    gotos_str = ",\n        ".join(gotos)
    return "m_states[" + str(state["index"]) \
        + "] = State {\n    { // actions\n      " + actions_str + "\n    }" \
        + ",\n    { // gotos \n        " + gotos_str + "\n    }\n  };"

def gen_nonterminal_to_strings(nonterminal):
    name, wildcard = nonterminal
    return "case Nonterminal::" + name + ": return \"" + name + "\";"

def gen_productions_to_strings(grammar):
    names = set()
    for name,productions in grammar["nonterminals"].items():
        for prodname,wildcard in productions.items():
            names.add(prodname)
    lines = map(lambda p: "case Production::" + p + ": return \"" + p \
                + "\";",
                names)
    return "\n    ".join(lines)

def gen_src(template, table, config):
    namespace_prefix = gen_namespace_prefix(config["namespace"])
    states = map(lambda x : gen_state(template, x, config), table["table"])
    states_text = "\n  ".join(states)
    nonterminals_to_strings = "\n    ".join(map(gen_nonterminal_to_strings,\
                                              table["grammar"]["nonterminals"]\
                                              .items()))
    return string.Template(string.Template(template) \
            .safe_substitute(namespace=namespace_prefix, states=states_text, \
                             state_count=len(table["table"]),\
                             nonterminals_to_strings=nonterminals_to_strings,\
                             productions_to_strings\
                             =gen_productions_to_strings(table["grammar"]),\
                             mangled_productions_src=\
                             gen_mangled_productions_src(table["grammar"]))) \
              .safe_substitute(config)

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("json")
    argparser.add_argument("config")
    argparser.add_argument("dest")

    args = argparser.parse_args()
    table = json.load(open(args.json, "r"),\
                      object_pairs_hook=collections.OrderedDict)
    config = json.load(open(args.config, "r"))
    dest = args.dest
    header_file = open(dest + "/include/" + config["class_name"] + ".hpp", "w+")
    src_file = open(dest + "/src/" + config["class_name"] + ".cpp", "w+")
    header_file.write(gen_header(header_template, table, config))
    src_file.write(gen_src(src_template, table, config))
    header_file.close()
    src_file.close()

if __name__ == '__main__':
    main()
