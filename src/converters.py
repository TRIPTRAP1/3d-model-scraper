"""Format conversion utilities for 3D models."""

from pathlib import Path
from typing import Optional

import trimesh
from loguru import logger

from .utils import format_bytes, get_file_size


class ModelConverter:
    """Convert 3D models between formats."""

    SUPPORTED_INPUT = {".gltf", ".glb", ".obj", ".ply", ".stl", ".dae"}
    SUPPORTED_OUTPUT = {".stl", ".obj", ".ply"}

    @staticmethod
    def get_file_format(filepath: Path) -> str:
        """
        Get format of a 3D model file.

        Args:
            filepath: Path to the model file

        Returns:
            Format extension (e.g., 'gltf', 'glb', 'stl')
        """
        return filepath.suffix.lower().lstrip(".")

    @staticmethod
    def is_supported(filepath: Path, file_type: str = "input") -> bool:
        """
        Check if file format is supported.

        Args:
            filepath: Path to the model file
            file_type: Either 'input' or 'output'

        Returns:
            True if format is supported
        """
        supported = (
            ModelConverter.SUPPORTED_INPUT
            if file_type == "input"
            else ModelConverter.SUPPORTED_OUTPUT
        )
        return filepath.suffix.lower() in supported

    @staticmethod
    def to_stl(
        input_path: Path,
        output_path: Optional[Path] = None,
        auto_orient: bool = True,
        simplify: bool = False,
        max_vertices: Optional[int] = None,
    ) -> Path:
        """
        Convert a 3D model to STL format.

        Args:
            input_path: Path to input model file
            output_path: Path for output STL file (default: same name, .stl extension)
            auto_orient: Whether to auto-orient the mesh
            simplify: Whether to simplify the mesh
            max_vertices: Maximum vertices for simplification (if enabled)

        Returns:
            Path to the output STL file

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If format is not supported
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if not ModelConverter.is_supported(input_path, "input"):
            raise ValueError(
                f"Unsupported input format: {input_path.suffix}. "
                f"Supported: {ModelConverter.SUPPORTED_INPUT}"
            )

        if output_path is None:
            output_path = input_path.with_suffix(".stl")

        input_size = format_bytes(get_file_size(input_path))
        logger.info(f"Converting {input_path.name} ({input_size}) to STL...")

        try:
            # Load the mesh
            mesh = trimesh.load(str(input_path), process=False)

            # Handle multiple meshes
            if isinstance(mesh, trimesh.Scene):
                logger.debug(f"Scene detected with {len(mesh.geometry)} meshes")
                if len(mesh.geometry) == 0:
                    raise ValueError("Scene contains no geometry")
                # Combine all meshes
                meshes = [geom for geom in mesh.geometry.values()]
                mesh = trimesh.util.concatenate(meshes)
            elif isinstance(mesh, list):
                logger.debug(f"Multiple meshes detected: {len(mesh)} meshes")
                mesh = trimesh.util.concatenate(mesh)

            # Clean up and validate
            if not mesh.is_valid:
                logger.warning("Mesh is invalid, attempting to fix...")
                mesh.remove_degenerate_faces()
                mesh.remove_duplicate_faces()
                mesh.remove_infinite_values()

            # Auto-orient if requested
            if auto_orient:
                logger.debug("Auto-orienting mesh...")
                mesh.invert()  # Ensure correct winding

            # Simplify if requested
            if simplify and max_vertices and len(mesh.vertices) > max_vertices:
                logger.info(
                    f"Simplifying mesh from {len(mesh.vertices)} to ~{max_vertices} vertices"
                )
                mesh = mesh.simplify_quadratic(target_count=max_vertices)

            # Export to STL
            output_path.parent.mkdir(parents=True, exist_ok=True)
            mesh.export(str(output_path), file_type="stl_ascii")

            output_size = format_bytes(get_file_size(output_path))
            logger.success(
                f"Converted to STL: {output_path.name} ({output_size}) "
                f"- Vertices: {len(mesh.vertices)}, Faces: {len(mesh.faces)}"
            )

            return output_path

        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            raise

    @staticmethod
    def convert(
        input_path: Path,
        output_format: str = "stl",
        output_path: Optional[Path] = None,
        **kwargs,
    ) -> Path:
        """
        Generic conversion between formats.

        Args:
            input_path: Path to input model file
            output_format: Target format (stl, obj, ply)
            output_path: Path for output file
            **kwargs: Additional arguments for specific converters

        Returns:
            Path to the output file
        """
        output_format = output_format.lower().lstrip(".")

        if output_format == "stl":
            return ModelConverter.to_stl(input_path, output_path, **kwargs)
        else:
            logger.error(f"Conversion to {output_format} not yet implemented")
            raise NotImplementedError(f"Conversion to {output_format} not supported yet")
