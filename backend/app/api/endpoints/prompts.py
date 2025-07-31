from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Body, status
from app.services.prompt_manager import PromptManager

router = APIRouter()

# Create a singleton instance of PromptManager
prompt_manager = PromptManager()


@router.get("/", response_model=List[Dict[str, Any]])
def list_prompts():
    """
    List all available prompts.
    """
    return prompt_manager.list_prompts()


@router.get("/{prompt_id}", response_model=Dict[str, Any])
def get_prompt(
        prompt_id: str = Path(..., description="The ID of the prompt to get")
):
    """
    Get a specific prompt by ID.
    """
    prompt_data = prompt_manager.prompts.get(prompt_id)
    if not prompt_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt with ID {prompt_id} not found"
        )

    return {
        "id": prompt_id,
        "template": prompt_data.get("template", ""),
        "input_variables": prompt_data.get("input_variables", []),
        "description": prompt_data.get("description", "")
    }


@router.post("/{prompt_id}", response_model=Dict[str, bool])
def update_prompt(
        prompt_id: str = Path(..., description="The ID of the prompt to update"),
        template: str = Body(..., description="The prompt template"),
        input_variables: List[str] = Body(..., description="The prompt input variables"),
        description: str = Body("", description="The prompt description")
):
    """
    Update or create a prompt.
    """
    success = prompt_manager.update_prompt(prompt_id, template, input_variables, description)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update prompt. The template may be invalid."
        )

    return {"success": True}


@router.delete("/{prompt_id}", response_model=Dict[str, bool])
def delete_prompt(
        prompt_id: str = Path(..., description="The ID of the prompt to delete")
):
    """
    Delete a prompt.
    """
    if prompt_id in ["qa", "conversational_qa", "condense_question"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete default prompts"
        )

    success = prompt_manager.delete_prompt(prompt_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt with ID {prompt_id} not found"
        )

    return {"success": True}