from django.core.management.base import BaseCommand
from SEMRinterface.models import Study, User, Case, Medication, CaseMedication
from SEMRinterface.services import (
    get_study_ids, load_json, get_user_details, load_case_details,
    get_case_files
)
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Load data from resources directory into database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Clear existing data before loading',
        )

    def handle(self, *args, **options):
        BASE_DIR = getattr(settings, "BASE_DIR", os.getcwd())
        RESOURCES_DIR = os.path.join(BASE_DIR, "resources")

        if options['reset']:
            self.stdout.write('Clearing existing data...')
            Study.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        study_ids = get_study_ids(RESOURCES_DIR)
        if not study_ids:
            self.stdout.write(self.style.WARNING('No studies found in resources directory.'))
            return

        total_studies = len(study_ids)
        self.stdout.write(f'Found {total_studies} studies to process.')

        for i, study_id in enumerate(study_ids, 1):
            self.stdout.write(f'Processing study {i}/{total_studies}: {study_id}')
            try:
                self._load_study(study_id, RESOURCES_DIR)
                self.stdout.write(f'  ✓ Study {study_id} loaded successfully')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Failed to load study {study_id}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Data loading completed.'))

    def _load_study(self, study_id, resources_dir):
        """Load a single study and all its related data."""
        study, created = Study.objects.get_or_create(
            study_id=study_id,
            defaults={
                'data_layout': load_json(os.path.join(resources_dir, study_id, 'data_layout.json')) or {},
                'variable_details': load_json(os.path.join(resources_dir, study_id, 'variable_details.json')) or {},
            }
        )
        if created:
            self.stdout.write(f'  Created study: {study_id}')
        else:
            self.stdout.write(f'  Study already exists: {study_id}')

        # Load users
        self._load_users(study, study_id, resources_dir)

        # Load medications
        self._load_medications(study, study_id, resources_dir)

        # Load cases
        self._load_cases(study, study_id, resources_dir)

    def _load_users(self, study, study_id, resources_dir):
        """Load users for a study."""
        user_details = get_user_details(study_id, resources_dir)
        if not user_details:
            self.stdout.write('  No user details found')
            return

        for user_id, user_data in user_details.items():
            defaults = {
                'cases_assigned': user_data.get('cases_assigned', []),
                'cases_completed': user_data.get('cases_completed', []),
            }
            last_accessed = user_data.get('last_accessed')
            if last_accessed is not None:
                try:
                    from django.utils.dateparse import parse_datetime
                    if isinstance(last_accessed, str):
                        parsed = parse_datetime(last_accessed)
                    elif isinstance(last_accessed, (int, float)):
                        import datetime
                        parsed = datetime.datetime.fromtimestamp(last_accessed / 1000)
                    else:
                        parsed = None
                    if parsed:
                        defaults['last_accessed'] = parsed
                except Exception as e:
                    self.stdout.write(f'    Warning: Could not parse last_accessed for user {user_id}: {e}')

            User.objects.get_or_create(
                study=study,
                user_id=user_id,
                defaults=defaults
            )

    def _load_medications(self, study, study_id, resources_dir):
        """Load medications for a study."""
        med_details = load_json(os.path.join(resources_dir, study_id, 'med_details.json'))
        if not med_details:
            self.stdout.write('  No medication details found')
            return

        for medidx, med_data in med_details.items():
            Medication.objects.get_or_create(
                study=study,
                medidx=medidx,
                defaults={
                    'display_name': med_data.get('display_name', ''),
                    'original_name': med_data.get('original_name', ''),
                    'med_route': med_data.get('med_route', ''),
                }
            )

    def _load_cases(self, study, study_id, resources_dir):
        """Load cases for a study."""
        case_details = load_json(os.path.join(resources_dir, study_id, 'case_details.json'))
        cases_dir = os.path.join(resources_dir, study_id, 'cases_all')

        if not os.path.exists(cases_dir):
            self.stdout.write('  No cases directory found')
            return

        for case_id in os.listdir(cases_dir):
            case_dir = os.path.join(cases_dir, case_id)
            if not os.path.isdir(case_dir):
                continue

            try:
                demographics = load_json(os.path.join(case_dir, 'demographics.json')) or {}
                observations = load_json(os.path.join(case_dir, 'observations.json')) or {}
                note_panel_data = load_json(os.path.join(case_dir, 'note_panel_data.json')) or {}
                case_detail = case_details.get(case_id, []) if case_details else []

                case, created = Case.objects.get_or_create(
                    study=study,
                    case_id=case_id,
                    defaults={
                        'demographics': demographics,
                        'observations': observations,
                        'note_panel_data': note_panel_data,
                        'case_details': case_detail,
                    }
                )

                # Load case medications
                self._load_case_medications(case, case_dir)

            except Exception as e:
                self.stdout.write(f'    Error loading case {case_id}: {e}')

    def _load_case_medications(self, case, case_dir):
        """Load medications for a specific case."""
        medications = load_json(os.path.join(case_dir, 'medications.json'))
        if not medications:
            return

        for medidx, med_data in medications.items():
            try:
                medication = Medication.objects.get(study=case.study, medidx=medidx)
                CaseMedication.objects.get_or_create(
                    case=case,
                    medication=medication,
                    defaults={
                        'med_data': med_data.get('med_data', []),
                        'y_axis_ranges': med_data.get('y_axis_ranges', []),
                    }
                )
            except Medication.DoesNotExist:
                self.stdout.write(f'    Warning: Medication {medidx} not found for case {case.case_id}')
            except Exception as e:
                self.stdout.write(f'    Error loading medication {medidx} for case {case.case_id}: {e}')

            # Load users
            user_details = get_user_details(study_id, RESOURCES_DIR)
            if user_details:
                for user_id, user_data in user_details.items():
                    defaults = {
                        'cases_assigned': user_data.get('cases_assigned', []),
                        'cases_completed': user_data.get('cases_completed', []),
                    }
                    last_accessed = user_data.get('last_accessed')
                    if last_accessed is not None:
                        try:
                            from django.utils.dateparse import parse_datetime
                            if isinstance(last_accessed, str):
                                parsed = parse_datetime(last_accessed)
                            elif isinstance(last_accessed, (int, float)):
                                # Assume timestamp in milliseconds
                                import datetime
                                parsed = datetime.datetime.fromtimestamp(last_accessed / 1000)
                            else:
                                parsed = None
                            if parsed:
                                defaults['last_accessed'] = parsed
                        except:
                            pass  # Skip invalid dates
                    User.objects.get_or_create(
                        study=study,
                        user_id=user_id,
                        defaults=defaults
                    )

            # Load medications
            med_details = load_json(os.path.join(RESOURCES_DIR, study_id, 'med_details.json'))
            if med_details:
                for medidx, med_data in med_details.items():
                    Medication.objects.get_or_create(
                        study=study,
                        medidx=medidx,
                        defaults={
                            'display_name': med_data.get('display_name', ''),
                            'original_name': med_data.get('original_name', ''),
                            'med_route': med_data.get('med_route', ''),
                        }
                    )

            # Load cases
            case_details = load_json(os.path.join(RESOURCES_DIR, study_id, 'case_details.json'))
            cases_dir = os.path.join(RESOURCES_DIR, study_id, 'cases_all')
            if os.path.exists(cases_dir):
                for case_id in os.listdir(cases_dir):
                    case_dir = os.path.join(cases_dir, case_id)
                    if os.path.isdir(case_dir):
                        demographics = load_json(os.path.join(case_dir, 'demographics.json')) or {}
                        observations = load_json(os.path.join(case_dir, 'observations.json')) or {}
                        note_panel_data = load_json(os.path.join(case_dir, 'note_panel_data.json')) or {}
                        case_detail = case_details.get(case_id, []) if case_details else []

                        case, created = Case.objects.get_or_create(
                            study=study,
                            case_id=case_id,
                            defaults={
                                'demographics': demographics,
                                'observations': observations,
                                'note_panel_data': note_panel_data,
                                'case_details': case_detail,
                            }
                        )

                        # Load case medications
                        medications = load_json(os.path.join(case_dir, 'medications.json'))
                        if medications:
                            for medidx, med_data in medications.items():
                                try:
                                    medication = Medication.objects.get(study=study, medidx=medidx)
                                    CaseMedication.objects.get_or_create(
                                        case=case,
                                        medication=medication,
                                        defaults={
                                            'med_data': med_data.get('med_data', []),
                                            'y_axis_ranges': med_data.get('y_axis_ranges', []),
                                        }
                                    )
                                except Medication.DoesNotExist:
                                    self.stdout.write(f"Medication {medidx} not found for study {study_id}")

        self.stdout.write(self.style.SUCCESS('Data loaded successfully'))