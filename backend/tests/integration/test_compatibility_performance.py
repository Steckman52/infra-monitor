import time
from datetime import datetime, timezone

from src.analysis.version_compatibility import compute_compatibility
from src.models.dependency import Dependency
from src.models.service import Service


def test_compatibility_computation_is_fast_at_scale(db_session):
    now = datetime.now(timezone.utc)
    services = []
    for i in range(200):
        service = Service(
            name=f"service-{i:04d}",
            ecosystem="node",
            repository_path=f"/repos/service-{i:04d}",
            manifest_path=f"/repos/service-{i:04d}/package.json",
            is_complete=True,
            last_scanned_at=now,
        )
        # Every service shares "lodash" at an alternating major version, so
        # the single resulting group is a genuine compatibility_risk and
        # every row has to be classified, not short-circuited.
        major = 4 if i % 2 == 0 else 3
        service.dependencies = [Dependency(name="lodash", declared_version=f"^{major}.0.0")]
        services.append(service)

    db_session.add_all(services)
    db_session.commit()

    start = time.perf_counter()
    groups = compute_compatibility(db_session)
    elapsed = time.perf_counter() - start

    assert len(groups) == 1
    assert groups[0].status == "compatibility_risk"
    assert elapsed < 1.0, f"compatibility computation took {elapsed:.3f}s, expected well under 1s"
