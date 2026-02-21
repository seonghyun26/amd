"""Entry point for the MD agent. Run with Hydra CLI overrides."""

from __future__ import annotations

import hydra
from omegaconf import DictConfig, OmegaConf

from md_agent.agent import MDAgent


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig) -> None:
    work_dir = cfg.run.work_dir
    agent = MDAgent(cfg=cfg, work_dir=work_dir)

    if cfg.mode == "run":
        target_name = OmegaConf.select(cfg, "method._target_name", default="enhanced sampling")
        system_name = OmegaConf.select(cfg, "system.name", default="system")
        prompt = (
            f"Run a {target_name} simulation for the {system_name} system. "
            f"Use all parameters defined in the loaded Hydra config. "
            f"Work directory: {work_dir}. "
            f"Initialize wandb, generate all input files, run grompp, "
            f"launch mdrun with the PLUMED input, start the background monitor, "
            f"wait for completion, then do a final wandb log and analysis."
        )
        result = agent.run(prompt)
        print(result)

    elif cfg.mode == "reproduce_paper":
        if cfg.paper.text:
            prompt = (
                f"Extract MD simulation parameters from the following paper text and "
                f"reproduce the simulation. Work directory: {work_dir}.\n\n"
                f"Paper text:\n{cfg.paper.text}"
            )
        elif cfg.paper.arxiv_id:
            prompt = (
                f"Find ArXiv paper {cfg.paper.arxiv_id}, extract its MD simulation "
                f"parameters, generate a Hydra config, and reproduce the simulation. "
                f"Work directory: {work_dir}. "
                f"Always show me the extracted config and ask for confirmation before running."
            )
        elif cfg.paper.query:
            prompt = (
                f"Search for papers about: '{cfg.paper.query}'. "
                f"Show me the top results, let me choose one, then extract its MD "
                f"simulation parameters and reproduce them. Work directory: {work_dir}. "
                f"Ask for confirmation before running the simulation."
            )
        elif cfg.paper.pdf_path:
            prompt = (
                f"Extract MD simulation parameters from the PDF at {cfg.paper.pdf_path}, "
                f"generate a Hydra config, and reproduce the simulation. "
                f"Work directory: {work_dir}. "
                f"Show me the extracted config and ask for confirmation before running."
            )
        else:
            raise ValueError(
                "reproduce_paper mode requires one of: "
                "paper.arxiv_id, paper.query, paper.pdf_path, or paper.text"
            )
        result = agent.run(prompt)
        print(result)

    elif cfg.mode == "interactive":
        print("MD Agent ready. Type your instructions (Ctrl+C or 'quit' to exit).")
        print(f"Working directory: {work_dir}\n")
        while True:
            try:
                user_input = input("You: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye.")
                break
            if user_input.lower() in ("quit", "exit", "q"):
                break
            if not user_input:
                continue
            response = agent.run(user_input)
            print(f"\nAgent: {response}\n")

    else:
        raise ValueError(
            f"Unknown mode '{cfg.mode}'. Expected: run | reproduce_paper | interactive"
        )


if __name__ == "__main__":
    main()
